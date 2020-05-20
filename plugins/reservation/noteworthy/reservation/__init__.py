import os
import docker
import re
import uuid

from better_profanity import profanity
from grpcz import grpc_controller, grpc_method
from clicz import cli_method
from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.reservation.proto.messages_pb2 import (
    ReservationRequest, ReservationResponse, LinkRequest, LinkResponse)

@grpc_controller
class ReservationController(NoteworthyPlugin):
    '''Manage reservations / invites for Noteworthy beta
    '''

    PLUGIN_NAME = 'reservation'
    DJANGO_APP_MODULE = 'noteworthy.reservation.api'
    DOMAIN_BLACKLIST = {
        'noteworthy.im': set([
            None, 'hub', 'get', 'git', 'www', 'support', 'docs', 'mail'])
    }

    def __init__(self):
        self._setup_django()

    @grpc_method(ReservationRequest, ReservationResponse)
    def reserve_domain(self, domain: str, auth_code: str):
        try:
            user = self._get_user_by_auth(auth_code)
            base_domain, subdomain = self._validate_domain(domain,
                                                           is_reservation=True)
            reservation = self._validate_reservation(user, base_domain, subdomain)
        except Exception as e:
            return {
                'success': None,
                'error' : str(e)
            }
        return {
            'success': f'{domain} reserved successfully',
            'error': None
        }

    @grpc_method(LinkRequest, LinkResponse)
    def create_link(self, domain: str, pub_key: str, auth_code: str):
        try:
            user = self._get_user_by_auth(auth_code)
            self._validate_domain(domain)
            labels = domain.split('.')
            base_domain = '.'.join(labels[-2:])
            subdomain = '.'.join(labels[-3:-2])
            reservation = self._check_reservation(user, base_domain, subdomain)
            matrix_domain = f'matrix.{domain}'
            link_domains = [domain, matrix_domain]
            dashed_domain = domain.replace('.', '-')
            link_name = f'link-{dashed_domain}'
            self._check_links(user, link_name)
            from noteworthy.hub import HubController
            hc = HubController()
            link_info = hc.provision_link(
                link_name=link_name, domains=link_domains, pub_key=pub_key)
            Link.objects.create(
                name = link_name, user=user, reservation=reservation,
                wg_endpoint = link_info['link_wg_endpoint'],
                udp_proxy_endpoint = link_info['link_udp_proxy_endpoint'],
                wg_pubkey = link_info['link_wg_pubkey'])
            link_info['error'] = None
        except Exception as e:
            link_info = {
                'user': None, 'reservation': None, 'wg_endpoint': None,
                'udp_proxy_endpoint': None, 'wg_pubkey': None, 'error': str(e)
            }
        return link_info

    def _get_user_by_auth(self, auth_code):
        from noteworthy.reservation.api.models import User
        if not isinstance(auth_code, uuid.UUID):
            auth_code = uuid.UUID(auth_code) # determine is valid uuid
        user = User.objects.get(auth_code=auth_code)
        return user

    def _validate_reservation(self, user, base_domain, subdomain):
        if subdomain in self.DOMAIN_BLACKLIST.get(base_domain, set()):
            raise Exception(f'Cannot reserve {subdomain}.{base_domain}')
        from noteworthy.reservation.api.models import Reservation
        user_reservations = Reservation.objects.filter(user=user)
        matching_reservation = user_reservations.filter(base_domain=base_domain,
                                                        subdomain=subdomain)
        reservation = None
        if matching_reservation.exists():
            reservation = matching_reservation[0]
        else:
            num_reservations = user_reservations.count()
            if user.num_reservations_allowed and (num_reservations >= user.num_reservations_allowed):
                raise Exception('User has reached domain reservation limit!')
            reservation = Reservation.objects.create(
                user=user, base_domain=base_domain, subdomain=subdomain)
        return reservation

    def _check_reservation(self, user, base_domain, subdomain):
        if subdomain in self.DOMAIN_BLACKLIST.get(base_domain, set()):
            raise Exception(f'Cannot use {subdomain}.{base_domain}')
        from noteworthy.reservation.api.models import Reservation
        user_reservations = Reservation.objects.filter(user=user)
        matching_reservation = user_reservations.filter(base_domain=base_domain,
                                                        subdomain=subdomain)
        if not matching_reservation.exists():
            raise Exception(
                f'{user} does not have {subdomain}.{base_domain} reserved!')
        return matching_reservation[0]

    def _validate_domain(self, domain, is_reservation=False):
        if not self._is_valid_hostname(domain):
            raise Exception('Domain must be a valid hostname')
        if profanity.contains_profanity(domain):
            raise Exception('Profanity Detected in domain.')
        labels = domain.split('.')
        base_domain = '.'.join(labels[-2:])
        subdomain = '.'.join(labels[:-2])
        if is_reservation and '.' in subdomain:
            raise Exception('Reserved domains must be of syntax: "sub.domain.tld"')
        return base_domain, subdomain

    def _is_valid_hostname(self, hostname):
        # empty string not valid
        if not hostname:
            return False
        # fqdn max length
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile(r'(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split('.'))

    def _check_links(self, user, link_name):
        from noteworthy.reservation.api.models import Link
        user_links = Link.objects.filter(user=user)
        distinct_links = set([link.name for link in user_links])
        if link_name in distinct_links:
            return
        if len(distinct_links) >= user.num_links_allowed:
            raise Error(f'{user} has reached link limit')

    def _setup_django(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'noteworthy.http_service.rest_api.rest_api.settings'
        import django
        django.setup()
        return django

    @cli_method
    def invite(self, email: str, max_reservations: int = 1):
        '''invite a user to the Noteworthy beta
        ---
        Args:
            email: Email of user to generate invite for
            max_reservations: Maximum number of allowed reservations (set to 0 for unlimited)
        '''
        from noteworthy.reservation.api.models import User
        User.objects.create_user(email, num_reservations_allowed=int(max_reservations))
        print(f"{email}: {User.objects.provision_auth_codes(1)[0].auth_code}")

    invite.clicz_aliases = ['invite']

Controller = ReservationController
