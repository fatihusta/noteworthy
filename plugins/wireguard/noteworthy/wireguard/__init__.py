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
    
    def start_hub(self):
        self.docker.containers.run('noteworthy-wireguard',
        name="wg-easy-hub",
        auto_remove=True,
        ports={'2222/tcp':None},
        volumes=['/opt/noteworthy/noteworth-wireguard/hub:/opt/noteworthy/noteworthy-wireguard/hub'],
        detach=True)

    def stop_hub(self):
        self.docker.containers.get('wg-easy-hub').stop()



Controller = WireGuardController