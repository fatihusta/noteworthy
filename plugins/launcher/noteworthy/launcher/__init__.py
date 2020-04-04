import shutil
from pathlib import Path

from noteworthy.notectl.plugins import NoteworthyPlugin


class LauncherController(NoteworthyPlugin):

    PLUGIN_NAME = 'launcher'

    PACKAGE_CACHE = '/var/noteworthy/cache/packages'

    def __init__(self):
        super().__init__(__file__)
        self.args = None

    def install(self, **kwargs):
        self.sub_parser.add_argument('--archive', help='path of archive to install')
        args = self.sub_parser.parse_known_args(self.args)[0]
        if args.archive:
            Path(self.PACKAGE_CACHE).mkdir(parents=True, exist_ok=True)
            shutil.unpack_archive(args.archive, self.PACKAGE_CACHE)
        print('Done.')


Controller = LauncherController
