from __future__ import print_function, unicode_literals

try:
    import ConfigParser as configparser
except ImportError:  # Python 3
    import configparser
import os
import os.path
import sys

__version__ = '0.2.1'

CONFIG_FILES = {'.gedrc', 'gedrc'}
CONFIG_FILES_LOCATIONS = {os.environ['HOME']}
CONFIG_DEFAULTS = {'scripts_dir': '~/scripts/'}

config = {}
commands = set()


def locate_config_file():
    for directory in CONFIG_FILES_LOCATIONS:
        for file_name in os.listdir(directory):
            if file_name in CONFIG_FILES:
                return os.path.join(directory, file_name)


def get_scripts_dir():
    scripts_dir = os.path.expanduser(config.get('scripts_dir'))
    sys.path.append(os.path.join(os.path.dirname(__file__),
                    scripts_dir))
    return scripts_dir


def verify_config_file():
    cfg = configparser.ConfigParser()
    cfg.read(locate_config_file())
    scripts_dir = cfg.get('settings', 'scripts_dir',
                          CONFIG_DEFAULTS['scripts_dir'])
    try:
        aliases = cfg.items('aliases')
    except configparser.NoSectionError:
        aliases = []
    config['scripts_dir'] = scripts_dir
    config['aliases'] = aliases


def get_commands():
    command_dir = get_scripts_dir()
    files = os.listdir(command_dir)
    for _file in files:
        if _file.endswith('.py'):
            commands.add(_file)


def execute_command(path, args):
    mod = __import__(path)
    sys.exit(mod.main(args))


def import_command(path):
    if path + '.py' in commands:
        execute_command(path, sys.argv[2:])
    else:
        # checking for aliases
        for alias, command in config['aliases']:
            if path == alias:
                command, args = command.split(' ')[0], command.split(' ')[1:]
                if not args:
                    args = sys.argv[2:]

                if command + '.py' in commands:
                    execute_command(command, args)
        raise LookupError('Cannot found: {}'.format(path))


def main(args=None):
    import argparse

    if args is None:
        args = sys.argv[1:]

    verify_config_file()
    get_scripts_dir()
    get_commands()

    parser = argparse.ArgumentParser(prog='ged')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-a', '--aliases', action='store_true')
    parser.add_argument('-v', '--version', action='version',
                        version=__version__)
    # this will contain the script/program name and any arguments for it.
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help=argparse.SUPPRESS)

    options = parser.parse_args(args)

    if options.list or not args:
        print('Available commands:')
        for command in commands:
            print('  -', command.split('.py')[0])

    elif options.aliases:
        print('Available aliases:')
        for alias, command in config['aliases']:
            print('  -', alias, '->', command)

    elif options.args:
        import_command(args[0])
