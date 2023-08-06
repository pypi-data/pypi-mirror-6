"""
Manage Pacific Apps from a command line.

Usage:
    pacific <command> <config>
    pacific -h | --help

Options:
    -h, --help       Show this screen.
    -V, --version    Show version.

The most commonly used commands are:
    run    Run a project instance.

"""
import configparser
from pkg_resources import get_distribution

import yaml
from docopt import docopt
from pyramid.scripts import pserve

from pacific import config as config_parser


def main():
    """ Entry point for the ``pacific`` command.
    """
    args = docopt(__doc__, argv=None, help=True,
                  version=get_distribution('Pacific'),
                  options_first=False)

    return COMMANDS[args['<command>']](args)


def cmd_run(args):
    """

    :param dict args:
    :return:
    """
    yaml_config = args['<config>']
    with open(yaml_config, 'r') as configfile:
        pconf = yaml.load(configfile.read())

    conf = configparser.ConfigParser()
    conf.read_string(DEV_CONFIG)

    conf['app:main']['pacific.superuser_id'] = str(pconf['superuser_id'])

    # Databases
    # ------------------------------------
    db_settings = config_parser.parse_db_settings(pconf['db'])
    conf['app:main'].update(db_settings)

    # Applications
    # ------------------------------------
    apps = config_parser.parse_apps(pconf['apps'])
    conf['app:main'].update({'apps': apps})

    # Applications' templates
    template_dirs = [conf['app:main']['mako.directories']]
    template_dirs.extend(['{}:templates'.format(app) for app in pconf['apps']])
    template_dirs = ' '.join(template_dirs)
    conf['app:main'].update({'mako.directories': template_dirs})

    compiled_config = '.{}.pconf'.format(yaml_config)
    with open(compiled_config, 'w') as configfile:
        conf.write(configfile)

    pserve_argv = ['pserve', compiled_config, '--reload']
    return pserve.main(pserve_argv)


COMMANDS = {
    'run': cmd_run
}


DEV_CONFIG = """
# -------------------------------
# app configuration
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/environment.html
# -------------------------------

[app:main]
use = egg:Pacific

pyramid.reload_templates = true
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.includes =
    pyramid_debugtoolbar
    pacific.plimdsl

# By default, the toolbar only appears for clients from IP addresses
# '127.0.0.1' and '::1'.
# debugtoolbar.hosts = 127.0.0.1 ::1

# Mako templates
mako.directories = pacific:templates
mako.input_encoding = utf-8

asset.static_prefix = https://localhost:34443/static/
asset.static_dev_prefix = https://localhost:34443/static/dev/

# i18n and l10n
# -------------------------------
pyramid.default_locale_name = en
available_languages = en de es ru

# -------------------------------
# wsgi server configuration
# -------------------------------

[server:main]
use = egg:waitress#main
host = 0.0.0.0
port = 8000
url_scheme = https

# -------------------------------
# logging configuration
# http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/logging.html
# -------------------------------

[loggers]
keys = root, pacific, sqlalchemy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_pacific]
level = DEBUG
handlers =
qualname = pacific

[logger_sqlalchemy]
level = INFO
handlers =
qualname = sqlalchemy.engine
# "level = INFO" logs SQL queries.
# "level = DEBUG" logs SQL queries and results.
# "level = WARN" logs neither.  (Recommended for production systems.)

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s
"""