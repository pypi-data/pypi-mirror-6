"""
Create a full db schema for the project.

Usage:
    pacific initdb

Options:
    -f, --force     force utility to initialize a database in an existing instance.

"""
import os
import subprocess
import yaml
from io import StringIO

from docopt import docopt

from pacific.db import get_session_factories


def main():
    sessions = get_session_factories({})
    SCHEMA_DIR = './db_schema'
    DB_SETTINGS_PATH = os.path.join(SCHEMA_DIR, 'common_settings.sql')

    # It seems like postgres caches locale data on server startup
    # and after that it cannot see any newly added locales in createdb script.
    # We should explicitly restart the server.
    # subprocess.Popen("sudo service postgresql restart", shell=True).communicate()

    # We'll walk through raw source catalogs and
    # compile target files according to build.yml configs.
    for working_dir in os.listdir(SCHEMA_DIR):
        working_path = os.path.join(SCHEMA_DIR, working_dir)
        if not os.path.isdir(working_path):
            continue
        try:
            with open(os.path.join(working_path, 'build.yml'), 'r') as f:
                config = yaml.load(f.read())
        except IOError:
            continue

        # Concatenate source files
        script_buffer = StringIO()
        for item in config['source']:
            item = "{}.sql".format(os.path.join(working_path, item))
            with open(item, 'rb') as f:
                script_buffer.write(f.read())
                # add extra linebreak to ensure that
                # instructions start from a newline.
                script_buffer.write('\n')

        # Execute scripts for each target
        for target in config['target']:
            # Drop previous DB instances
            subprocess.Popen(
                "dropdb -e -U {user} {database}".format(
                    user=target['user'],
                    database=target['database']
                ),
                shell=True
            ).communicate()

            # Create a new DB instance
            subprocess.Popen(
                "createdb -U {user} -l {locale} -E {encoding} "
                "-O {user} -T {template} {database}".format(
                    user=target['user'],
                    locale=target.get('locale', 'en_US.UTF-8'),
                    encoding=target.get('encoding', 'UTF-8'),
                    template=target.get('template', 'template0'),
                    database=target['database']
                ),
                shell=True
            ).communicate()

            # Set common settings
            subprocess.Popen(
                "psql -U {user} {database} -f {file}".format(
                    user=target['user'],
                    database=target['database'],
                    file=DB_SETTINGS_PATH
                ),
                shell=True
            ).communicate()

            # Extensions
            for ext in config.get('extensions', []):
                subprocess.Popen(
                    'sudo -u postgres psql {database} '
                    '-c "CREATE EXTENSION IF NOT EXISTS '
                    '{ext} WITH SCHEMA {user};"'.format(
                        user=target['user'],
                        database=target['database'],
                        ext=ext
                    ),
                    shell=True
                ).communicate()

            # Create tables
            ddl = "BEGIN;\n{ddl}\n".format(ddl=script_buffer.getvalue())
            ddl += (
                "REVOKE ALL ON SCHEMA {user} FROM postgres;"
                "GRANT ALL ON SCHEMA {user} TO postgres;"
                "COMMIT;"
            ).format(user=target['user'])

            subprocess.Popen(
                "psql -U {user} {database}".format(
                    user=target['user'],
                    database=target['database']
                ),
                shell=True,
                stdin=subprocess.PIPE
            ).communicate(ddl)
