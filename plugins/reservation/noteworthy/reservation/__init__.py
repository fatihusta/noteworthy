import os
import docker
import re
import uuid

from better_profanity import profanity
from grpcz import grpc_controller, grpc_method
from noteworthy.notectl.plugins import NoteworthyPlugin
from noteworthy.reservation.proto.messages_pb2 import (ReservationRequest, ReservationResponse)

@grpc_controller
class ReservationController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-reservation'
    DJANGO_APP_MODULE = 'noteworthy.reservation.api'

    def __init__(self):
        self._setup_django()

    @grpc_method(ReservationRequest, ReservationResponse)
    def reserve_domain(self, domain: str, pub_key: str, auth_code: str):
        user = self._get_user_by_auth(auth_code)
        base_domain, subdomain = self._validate_domain(domain)
        reservation = self._validate_reservation(user, base_domain, subdomain)
        reserved_domain = '.'.join([subdomain, base_domain])
        matrix_domain = '.'.join(['matrix', reserved_domain])
        link_domains = [reserved_domain, matrix_domain]
        from noteworthy.hub import HubController
        hc = HubController()
        link_name = f'link-reservation-{reservation.id}'
        link_info = hc.provision_link(
            link_name=link_name, domains=link_domains, pub_key=pub_key)
        from noteworthy.reservation.api.models import Link
        Link.objects.create(
            user=user, reservation=reservation,
            wg_endpoint = link_info['link_wg_endpoint'],
            udp_proxy_endpoint = link_info['link_udp_proxy_endpoint'],
            wg_pubkey = link_info['link_wg_pubkey'])
        return link_info

    def _get_user_by_auth(self, auth_code):
        from noteworthy.reservation.api.models import User
        if not isinstance(auth_code, uuid.UUID):
            auth_code = uuid.UUID(auth_code) # determine is valid uuid
        user = User.objects.get(auth_code=auth_code)
        return user

    def _validate_reservation(self, user, base_domain, subdomain):
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

    def _validate_domain(self, domain):
        if not self._is_valid_hostname(domain):
            raise Error('Domain must be a valid hostname')
        if profanity.contains_profanity(domain):
            raise Error('Profanity Detected in domain.')
        labels = domain.split('.')
        base_domain = '.'.join(labels[-2:])
        subdomain = '.'.join(labels[:-2])
        if '.' in subdomain:
            raise Error('Reserved domains must be of syntax: "sub.domain.tld"')
        if (not subdomain) and (base_domain == 'noteworthy.im'):
            raise Error('Cannot reserve noteworthy.im')
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

    def _setup_django(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'noteworthy.http_service.rest_api.rest_api.settings'
        import django
        django.setup()
        return django

Controller = ReservationController
