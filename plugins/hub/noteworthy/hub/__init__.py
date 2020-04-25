import os
from noteworthy.notectl.plugins import NoteworthyPlugin
import docker
from noteworthy.wireguard import wg
import yaml

class HubController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-hub'


    def __init__(self):
        super().__init__(__file__)
        self.docker = docker.from_env()

    def start(self):
        if self.is_first_run:
            self.create_config_dir()

    def provision_link(self, link_name: str, domain: str, pub_key: str, sites: str):
        domain_regex = self._validate_domain_regex(domain, sites)
        link_node = self._get_or_create_link(link_name, domain_regex, pub_key)
        link_wg_pubkey = link_node.exec_run('notectl wireguard pubkey').output.decode().strip()
        link_wg_port = link_node.attrs['NetworkSettings']['Ports']['18521/udp'][0]['HostPort']
        link_udp_proxy_port = link_node.attrs['NetworkSettings']['Ports']['18522/udp'][0]['HostPort']
        link_ip = link_node.attrs['NetworkSettings']['Networks']['noteworthy']['IPAddress']
        nc = NginxController()
        domain_match = domain.replace('.', '\\.')
        all_subdomains = f'~*^(.+\\.)?{domain_match}$'
        nc.add_tls_stream_backend(link_name, all_subdomains, link_ip)
        nc.set_http_proxy_pass(link_name, all_subdomains, link_ip)
        return {
            "link_wg_endpoint": f"{os.environ['NOTEWORTHY_HUB']}:{link_wg_port}",
            "link_udp_proxy_endpoint": f"{os.environ['NOTEWORTHY_HUB']}:{link_udp_proxy_port}",
            "link_wg_pubkey": link_wg_pubkey}

    def _validate_domain_regex(self, domain, sites):
        sites = [site.strip() for site in sites.split(';') if site.strip()]
        #TODO: check sites are all slugs!
        #TODO: check domain is a valid domain ('.' separated slugs)!!!
        piped_sites = '|'.join(sites)
        piped_sites_match = piped_sites.replace('.', '\\.')
        domain_match = domain.replace('.', '\\.')
        domain_regex = f'~*^(({piped_sites_match})\\.)?{domain_match}$'
        return domain_regex

    def _get_or_create_link(self, link_name, domain_regex, pub_key):
        try:
            link_node = self.docker.containers.get(link_name)
        except docker.errors.NotFound:
            return self._create_link_from_config(link_name, domain_regex, pub_key)

        try:
            current_config = self._read_yaml_config(link_name)
        except IOError:
            if link_node.status == 'running':
                link_node.stop()
            link_node.remove()
            return self._create_link_from_config(link_name, domain_regex, pub_key)

        does_match = self._does_match_config(current_config, domain_regex, pub_key)
        if not does_match:
            if link_node.status == 'running':
                link_node.stop()
            link_node.remove()
            link_node = self._create_link_from_config(link_config)
        return link_node

    def _does_match_config(self, current_config, domain_regex, pub_key):
        return (current_config.get('pub_key') == pub_key) and (current_config.get('domain_regex') == domain_regex)

    def _create_link_from_config(self, link_name, domain_regex, pub_key):
        link_node = self.docker.containers.run(
            f'noteworthy-launcher:DEV',
            tty=True,
            cap_add=['NET_ADMIN'],
            network='noteworthy',
            stdin_open=True,
            name=link_name,
            #auto_remove=True,
            ports={
                '18521/udp': None, # random wireguard port
                '18522/udp': None # random udp proxy port
            },
            detach=True,
            environment={
                'NOTEWORTHY_ROLE': 'link',
                'NOTEWORTHY_DOMAIN_REGEX': domain_regex,
                'TAPROOT_PUBKEY': pub_key
            },
            restart_policy={"Name": "always"})
        self._write_yaml_config(link_name, {
            'domain_regex': domain_regex,
            'pub_key': pub_key
        })
        return link_node

    def _read_yaml_config(self, filename):
        file_path = os.path.join(self.config_dir, f'{filename}.yaml')
        with open(file_path, 'r') as f:
            res = yaml.safe_load(f.read())
        return res

    def _write_yaml_config(self, filename, data):
        file_path = os.path.join(self.config_dir, f'{filename}.yaml')
        with open(file_path, 'w') as f:
            f.write(yaml.dump(data))
        return file_path

Controller = HubController
