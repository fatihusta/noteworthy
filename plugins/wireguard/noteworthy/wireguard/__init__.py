import docker
import os 

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
        image = self.docker.images.build(path=dockerfile_path, tag='noteworthy-wireguard')
        print('Done.')
        print()


Controller = WireGuardController