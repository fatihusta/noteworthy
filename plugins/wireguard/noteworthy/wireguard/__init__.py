import docker
import os
import sys

import getpass

dir_path = os.path.dirname(os.path.realpath(__file__))


class WireGuardController:
    def __init__(self):
        self.docker = docker.from_env()

    def init(self):
        print('Building WireGuard container.')
        print('This may take a few minutes.')
        dockerfile_path=os.path.join(dir_path, 'deploy/')
        #TODO debug print(dockerfile_path)
        #TODO write image build to log directory to help with debugging
        image = self.docker.images.build(path=dockerfile_path, tag='noteworthy-wireguard:latest')
        print('Done.')
        print()
    
    def start_hub(self):
        hub_pass = getpass.getpass('Set hub password: ')
        hub_pass_confirm = getpass.getpass('Confirm hub password: ')
        if hub_pass != hub_pass_confirm:
            print('Passwords did not match! Please try again.')
            sys.exit(1)
        # TODO make sure we meet default Linux password policy
        # TODO Allow user to select password or pubkey based auth
        self.docker.containers.run('noteworthy-wireguard:latest',
        tty=True,
        stdin_open=True,
        environment=[f'HUB_PASSWORD={hub_pass}'],
        name="wg-easy-hub",
        auto_remove=True,
        ports={'22/tcp':None},
        volumes=['/opt/noteworthy/noteworth-wireguard/hub:/opt/noteworthy/noteworthy-wireguard/hub'],
        detach=True)

    def stop_hub(self):
        self.docker.containers.get('wg-easy-hub').stop()



Controller = WireGuardController