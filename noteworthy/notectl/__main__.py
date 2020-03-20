#   _   _  ____ _______ ________          ______  _____ _______ _    ___     __
#  | \ | |/ __ |__   __|  ____\ \        / / __ \|  __ |__   __| |  | \ \   / /
#  |  \| | |  | | | |  | |__   \ \  /\  / | |  | | |__) | | |  | |__| |\ \_/ / 
#  | . ` | |  | | | |  |  __|   \ \/  \/ /| |  | |  _  /  | |  |  __  | \   /  
#  | |\  | |__| | | |  | |____   \  /\  / | |__| | | \ \  | |  | |  | |  | |   
#  |_| \_|\____/  |_|  |______|   \/  \/   \____/|_|  \_\ |_|  |_|  |_|  |_|  
import sys
import argparse

from noteworthy.notectl.cli import NoteworthyCLI


def main():
    arg_parser = argparse.ArgumentParser()

    cli = NoteworthyCLI(arg_parser)

    if cli.args.command == 'help':
        arg_parser.print_help()
        sys.exit(1)

    cli.dispatch()

    sys.exit(0)