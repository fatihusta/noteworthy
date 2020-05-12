import os
import re
import subprocess
import time

import docker
import yaml

from noteworthy.notectl.plugins import NoteworthyPlugin


class HubController(NoteworthyPlugin):

    PLUGIN_NAME = 'noteworthy-hub'


    def __init__(self):
        super().__init__(__file__)
        self.docker = docker.from_env()

    def start(self):
        if self.is_first_run:
            self.create_config_dir()
        else:
            self._restart_links()

    def provision_link(self, link_name: str, domains: list, pub_key: str):
        domain_regex = self._validate_domain_regex(domains)
        link_node = self._get_or_create_link(link_name, domain_regex, pub_key)
        link_wg_port = link_node.attrs['NetworkSettings']['Ports']['18521/udp'][0]['HostPort']
        link_udp_proxy_port = link_node.attrs['NetworkSettings']['Ports']['18522/udp'][0]['HostPort']
        link_ip = link_node.attrs['NetworkSettings']['Networks']['noteworthy']['IPAddress']
        from noteworthy.nginx import NginxController
        nc = NginxController()
        nc.add_tls_stream_backend(link_name, domain_regex, link_ip)
        nc.set_http_proxy_pass(link_name, domain_regex, link_ip)
        return {
            "link_wg_endpoint": f"{os.environ['NOTEWORTHY_HUB']}:{link_wg_port}",
            "link_udp_proxy_endpoint": f"{os.environ['NOTEWORTHY_HUB']}:{link_udp_proxy_port}",
            "link_wg_pubkey": link_wg_pubkey}

    def _validate_domain_regex(self, domains):
        for domain in domains:
            if not self._is_valid_hostname(domain):
                raise Exception(f'Invalid domain syntax: {domain}')
        piped_domains = '|'.join(domains)
        piped_domains_match = piped_domains.replace('.', '\\.')
        domain_regex = f'~^({piped_domains_match})$'
        return domain_regex

    def _is_valid_hostname(self, hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] # strip exactly one dot from the right, if present
        allowed = re.compile(r'(?!-)[A-Z\d-]{1,63}(?<!-)$', re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split('.'))

    def _get_or_create_link(self, link_name, domain_regex, pub_key, wg_port=None, udp_proxy_port=None):
        try:
            current_config = self._read_yaml_config(link_name)
            does_match = self._does_match_config(current_config, domain_regex, pub_key)
            if not does_match:
                try:
                    link_node = self.docker.containers.get(link_name)
                    link_node.remove(force=True)
                except docker.errors.NotFound:
                    link_wg_key, link_wg_pubkey = self._gen_link_wg_keys()
                    return self._create_link_from_config(link_name, domain_regex, pub_key, link_wg_key,
                                                            link_wg_pubkey, wg_port, udp_proxy_port)
            else:
                try:
                    link_node = self.docker.containers.get(link_name)
                    return link_node
                except docker.errors.NotFound:
                    link_wg_key, link_wg_pubkey = self._gen_link_wg_keys()
                    return self._create_link_from_config(link_name, domain_regex, pub_key, link_wg_key,
                                                            link_wg_pubkey, wg_port, udp_proxy_port)
        except IOError:
            try:
                link_node = self.docker.containers.get(link_name)
                link_node.remove(force=True)
            except docker.errors.NotFound:
                link_wg_key, link_wg_pubkey = self._gen_link_wg_keys()
                return self._create_link_from_config(link_name, domain_regex, pub_key, link_wg_key,
                                                                    link_wg_pubkey, wg_port, udp_proxy_port)
            return link_node

    def _gen_link_wg_keys(self):
        link_wg_key = subprocess.check_output(['wg', 'genkey']).strip()
        wg_pubkey_proc = subprocess.Popen(['wg', 'genkey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        link_wg_pubkey = wg_pubkey_proc.communicate(link_wg_key)[0].strip().decode()
        return link_wg_key, link_wg_pubkey

    def _does_match_config(self, current_config, domain_regex, pub_key):
        return (current_config.get('pub_key') == pub_key) and (current_config.get('domain_regex') == domain_regex)

    def _create_link_from_config(self, link_name, domain_regex, pub_key, link_wg_key, link_wg_pubkey, wg_port=None, udp_proxy_port=None):
        release_tag = self._load_release_tag()
        link_node = self.docker.containers.run(
            f'decentralabs/noteworthy:hub-{release_tag}',
            tty=True,
            cap_add=['NET_ADMIN'],
            network='noteworthy',
            stdin_open=True,
            name=link_name,
            #auto_remove=True,
            entrypoint='notectl link start',
            ports={
                '18521/udp': wg_port,
                '18522/udp': udp_proxy_port
            },
            detach=True,
            environment={
                'NOTEWORTHY_ROLE': 'link',
                'NOTEWORTHY_DOMAIN_REGEX': domain_regex,
                'TAPROOT_PUBKEY': pub_key,
                'LINK_WG_KEY': link_wg_key
            },
            restart_policy={"Name": "always"})

        # wait for container to enter running state before continuing
        count = 0
        while link_node.status != 'running' and count < 5:
            time.sleep(1)
            link_node = self.docker.containers.get(link_name)
            if link_node.status == 'running':
                wg_port = link_node.attrs['NetworkSettings']['Ports']['18521/udp'][0]['HostPort']
                udp_proxy_port = link_node.attrs['NetworkSettings']['Ports']['18522/udp'][0]['HostPort']
                self._write_yaml_config(link_name, {
                    'domain_regex': domain_regex,
                    'pub_key': pub_key,
                    'wg_port': wg_port,
                    'udp_proxy_port': udp_proxy_port,
                    'link_wg_key': link_wg_key,
                    'link_wg_pubkey': link_wg_pubkey
                })
                return self.docker.containers.get(link_name)
            count = count + 1
        raise Exception('Timeout exceeding waiting for link to enter running state.')

    def _restart_links(self):
        # TODO this works because only link.yaml files are in the config atm
        link_names = [link_file.replace('.yaml', '')
                      for link_file in os.listdir(self.config_dir)]
        links = [dict(self._read_yaml_config(link_name), name=link_name)
                 for link_name in link_names]
        for link in links:
            self._get_or_create_link(link['name'], link['domain_regex'],
                                     link['pub_key'], link['link_wg_key'],
                                     link['wg_port'], link['udp_proxy_port'])

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

    def _load_release_tag(self):
        with open('/opt/noteworthy/release', 'r') as tag_file:
            return tag_file.read().strip()

Controller = HubController
