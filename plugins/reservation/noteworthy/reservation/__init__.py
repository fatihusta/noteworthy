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
        base_domain, subdomain, site = self._validate_domain(domain)
        link, sites = self._validate_reservation(user, base_domain, subdomain, site)
        delimited_sites = ';'.join([site.site for site in sites])
        from noteworthy.hub import HubController
        hc = HubController()
        link_info = hc.provision_link(
            link_name=f'link-{link.id}', domain=link.domain, pub_key=pub_key,
            sites=delimited_sites)
        return link_info

    def _get_user_by_auth(self, auth_code):
        from noteworthy.reservation.api.models import BetaUser
        if not isinstance(auth_code, uuid.UUID):
            auth_code = uuid.UUID(auth_code) # determine is valid uuid
        user = BetaUser.objects.get(beta_key=auth_code)
        return user

    def _validate_reservation(self, user, base_domain, subdomain, site):
        from noteworthy.reservation.api.models import BetaLink, BetaSite
        user_links = BetaLink.objects.filter(beta_user=user)
        matching_link = user_links.filter(base_domain=base_domain, subdomain=subdomain)
        link = None
        if matching_link.exists():
            link = matching_link[0]
        else:
            num_links = user_links.count()
            if user.num_links_allowed and (num_links >= user.num_links_allowed):
                raise Exception('User has reached link limit.')
            link = BetaLink.objects.create(beta_user=user, base_domain=base_domain, subdomain=subdomain)
        matching_site = BetaSite.objects.filter(beta_link=link, site=site)
        if not matching_site.exists():
            user_sites = BetaSite.objects.filter(beta_user=user)
            num_sites = user_sites.count()
            if user.num_sites_allowed and (num_sites >= user.num_sites_allowed):
                raise Exception('User has reached site limit.')
            BetaSite.objects.create(beta_user=user, beta_link=link, site=site)
        link_sites = BetaSite.objects.filter(beta_link=link)
        return link, link_sites

    def _validate_domain(self, domain):
        if not self._is_valid_hostname(domain):
            raise Error('Domain must be a valid hostname')
        if profanity.contains_profanity(domain):
            raise Error('Profanity Detected in domain.')
        labels = domain.split('.')
        base_domain = '.'.join(labels[-2:])
        subdomain = '.'.join(labels[-3:-2])
        site = '.'.join(labels[:-3])
        if (not subdomain) and (base_domain == 'noteworthy.im'):
            raise Error('Cannot reserve noteworthy.im')
        return base_domain, subdomain, site



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
