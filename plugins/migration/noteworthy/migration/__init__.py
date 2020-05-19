import os
import yaml
import pkgutil
import importlib
from clicz import cli_method
from noteworthy.notectl.plugins import NoteworthyPlugin


class MigrationController(NoteworthyPlugin):

    PLUGIN_NAME = 'migration'

    def __init__(self):
        super().__init__(__file__)

    def start(self):
        print('starting Noteworthy migrations...')
        self.create_config_dir(clean=False)
        migrations = self._get_migrations()
        applied = self._get_applied()
        ordered_migrations = sorted(migrations, key=self._get_migration_number)
        completed = []
        for migration in ordered_migrations:
            name = migration.__name__
            if name in applied:
                print(f'\t{name} already applied.')
            else:
                print(f'\tApplying {name}...')
                try:
                    migration.run_migration()
                except Exception as e:
                    print(f'\t\tmigration failed:\n\t\t\t{repr(e)}\n\t\texiting...')
                    break
            completed.append(name)
        self._set_applied(completed)
        print('completed running Noteworthy migrations.')

    @cli_method
    def migrate(self):
        '''Run Noteworthy Migration Scripts
        '''
        self.start()

    def _get_migrations(self):
        m = []
        from . import migrations as MIGRATIONS
        prefix = MIGRATIONS.__name__ + "."
        for _, modname, __ in pkgutil.iter_modules(MIGRATIONS.__path__, prefix):
            m.append(importlib.import_module(modname))
        return m

    def _get_migration_number(self, migration_module):
        name = migration_module.__name__
        return name.split('.')[-1].split('_')[0]

    def _get_applied(self):
        file_path = os.path.join(self.config_dir, 'applied.yaml')
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                res = yaml.safe_load(f.read())
                return res or []
        return []

    def _set_applied(self, migrations):
        file_path = os.path.join(self.config_dir, 'applied.yaml')
        with open(file_path, 'w') as f:
            f.write(yaml.dump(migrations))


Controller = MigrationController
