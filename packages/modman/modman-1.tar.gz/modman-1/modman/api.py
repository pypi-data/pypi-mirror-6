import inspect
import json
import os

import docopt
import requests
import patoolib

from . import util

__all__ = [
    'add_game',
    'add_mod',
    'install',
    'uninstall',
]
__version__ = '1'
__doc__ = '''modman.

Usage:
    modman add game <name> <location>
    modman add mod <name> <url> [<installer>] [<installer-options>...]
    modman install <game-name> <mod-name>
    modman uninstall <game-name> <mod-name>

Options:
    -h, --help      Show this help.
    -v, --version   Show version.
'''

BASE_DIR = os.path.expanduser('~/.modman/')
DATABASE_FILE = os.path.join(BASE_DIR, 'db.json')
HANDLERS = []
to_arg = lambda arg: '<{}>'.format(arg.replace('_', '-'))


def handler(func):
    HANDLERS.append((
        func.__name__.split('_'),
        func,
        inspect.getfullargspec(func).args
    ))


def read_database():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE) as fobj:
            database = json.load(fobj)
    else:
        database = {'games': {}, 'mods': {}}
    return database


def write_database(database):
    with open(DATABASE_FILE, 'w') as fobj:
        json.dump(database, fobj)


@handler
def add_game(name, location):
    database = read_database()
    database['games'][name] = {
        'location': os.path.abspath(location),
        'installed_mods': {},
    }
    write_database(database)


@handler
def add_mod(name, url, installer=None, installer_options=None):
    database = read_database()
    database['mods'][name] = {
        'url': url,
        'installer': installer or 'modman.util.default_installer',
        'installer_options': installer_options or [],
    }
    write_database(database)


@handler
def install(game_name, mod_name):
    database = read_database()
    if game_name not in database['games']:
        raise ValueError(
            "Game {} not found, add via `modman add game`".format(game_name)
        )
    if mod_name not in database['mods']:
        raise ValueError(
            "Mod {} not found, add via `modman add mod`".format(mod_name)
        )
    installer = util.load(database['mods'][mod_name]['installer'])
    installer_options = database['mods'][mod_name]['installer_options']
    game_location = database['games'][game_name]['location']
    with util.tempdir() as download_dir:
        url = database['mods'][mod_name]['url']
        extension = util.guess_extension(url)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        archive = os.path.join(download_dir, 'archive{}'.format(extension))
        with open(archive, 'wb') as fobj:
            while True:
                chunk = response.raw.read(10240)
                if chunk:
                    fobj.write(chunk)
                else:
                    break
        with util.tempdir() as workspace:
            patoolib.extract_archive(archive, verbosity=-1, outdir=workspace)
            files = installer(workspace, game_location, *installer_options)
    database['games'][game_name]['installed_mods'][mod_name] = files
    write_database(database)


@handler
def uninstall(game_name, mod_name):
    database = read_database()
    if game_name not in database['games']:
        raise ValueError(
            "Game {} not found, add via `modman add game`".format(game_name)
        )
    if mod_name not in database['mods']:
        raise ValueError(
            "Mod {} not found, add via `modman add mod`".format(mod_name)
        )
    if mod_name not in database['games'][game_name]['installed_mods']:
        raise ValueError(
            "Mod {} not installed in {}".format(mod_name, game_name)
        )
    files = database['games'][game_name]['installed_mods'][mod_name]
    for filename in files:
        os.remove(filename)
    del database['games'][game_name]['installed_mods'][mod_name]
    write_database(database)


def cli():
    args = docopt.docopt(__doc__, version=__version__)
    for flags, func, argspec in HANDLERS:
        if all(args.get(flag, False) for flag in flags):
            return func(**{spec: args[to_arg(spec)] for spec in argspec})
