import sys


from noteworthy.notectl.plugins import PluginManager


class NoteworthyController(PluginManager):

    version_string = '0.0.2'

    def version(self):
        print('''
   _   _  ____ _______ ________          ______  _____ _______ _    ___     __
  | \ | |/ __ |__   __|  ____\ \        / / __ \|  __ |__   __| |  | \ \   / /
  |  \| | |  | | | |  | |__   \ \  /\  / | |  | | |__) | | |  | |__| |\ \_/ / 
  | . ` | |  | | | |  |  __|   \ \/  \/ /| |  | |  _  /  | |  |  __  | \   /  
  | |\  | |__| | | |  | |____   \  /\  / | |__| | | \ \  | |  | |  | |  | |   
  |_| \_|\____/  |_|  |______|   \/  \/   \____/|_|  \_\ |_|  |_|  |_|  |_|  
 ''')
        print('by Decentralabs - https://decentralabs.io')
        print()
        print(f'Version: {self.version_string}')
    
    def dispatch(self, command, *args, **kwargs):
        '''Proxy method invocation to self and plugins
        '''
        if command in self.plugins:
            plugin = command
            command = args[0]
            print(command)
            NoteworthyController._invoke_method(self.plugins[plugin], command)
            sys.exit(0)
        NoteworthyController._invoke_method(self, command)

    @staticmethod
    def _invoke_method(target, method):
        method = getattr(target, method)
        method()