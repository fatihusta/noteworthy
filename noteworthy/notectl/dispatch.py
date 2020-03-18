import sys


from noteworthy.notectl.plugins import PluginManager


class NoteworthyController(PluginManager):

    version_string = '0.0.1'

    def version(self):
        print('''
   _   _  ____ _______ ________          ______  _____ _______ _    ___     __
  | \ | |/ __ |__   __|  ____\ \        / / __ \|  __ |__   __| |  | \ \   / /
  |  \| | |  | | | |  | |__   \ \  /\  / | |  | | |__) | | |  | |__| |\ \_/ / 
  | . ` | |  | | | |  |  __|   \ \/  \/ /| |  | |  _  /  | |  |  __  | \   /  
  | |\  | |__| | | |  | |____   \  /\  / | |__| | | \ \  | |  | |  | |  | |   
  |_| \_|\____/  |_|  |______|   \/  \/   \____/|_|  \_\ |_|  |_|  |_|  |_|  
 ''')
        print(f'Version: {self.version_string}')
    
    def dispatch(self, command, *args, **kwargs):
        method = getattr(self, command)
        method()
