#!/usr/bin/env python

from __future__ import print_function

import copy
import os
import re
import subprocess
import sys

try:
    from configparser import Error as ConfigParserError, SafeConfigParser
except ImportError:
    from ConfigParser import Error as ConfigParserError, SafeConfigParser

from distutils.util import strtobool


__author__ = 'Igor Davydenko'
__license__ = 'BSD License'
__script__ = 'bootstrapper'
__version__ = '0.1.6'


CONFIG = {
    __script__: {},
    'pip': {
        'download_cache': '~/.{0}/pip-cache/'.format(__script__),
    },
    'virtualenv': {
        'distribute': True,
    }
}
DEFAULT_CONFIG = 'bootstrap.cfg'
DEFAULT_ENV = 'env'
DEFAULT_REQUIREMENTS = 'requirements.txt'
IS_PY3 = sys.version_info[0] == 3
REQUIREMENTS_RE = lambda pre, post: (
    re.compile(r'{0}-(.*).{1}'.format(pre, post))
)

iteritems = lambda seq: seq.items() if IS_PY3 else seq.iteritems()
string_types = (bytes, str) if IS_PY3 else basestring


class Environment(object):
    """
    Simple instance that represent virtual environment.
    """
    def __init__(self, dest, config):
        """
        Initialize virtual environment instance.
        """
        self.config = config
        self.bootstrap = bootstrap = config[__script__]

        if isinstance(dest, (list, tuple)):
            self.dest, self.requirements = dest
        else:
            self.dest = dest
            pre, post = bootstrap['requirements'].rsplit('.', 1)
            self.requirements = '{0}-{1}.{2}'.format(pre, dest, post)

        self.env = '{0}{1}'.format(
            bootstrap['env'], '-{0}'.format(self.dest) if self.dest else ''
        )

    def all_ok(self):
        """
        Print "All OK!" message.
        """
        if not self.bootstrap['quiet']:
            print('All OK!')

    def create(self):
        """
        Create virtual environment.
        """
        cmd = None

        if not self.bootstrap['quiet']:
            print('== Step 1. Create virtual environment ==')

        if self.is_minor and self.bootstrap.get('copy_virtualenv'):
            if not os.path.isdir(self.env):
                cmd = ('virtualenv-clone {0} {1}'.
                       format(self.bootstrap['env'], self.env))
        elif (
            self.bootstrap['recreate_virtualenv'] or
            not os.path.isdir(self.env)
        ):
            config = self.prepare_config(self.config['virtualenv'])
            args = ' '.join(config_to_args(config))
            cmd = 'virtualenv {0} {1}'.format(args, self.env)

        if not cmd and not self.bootstrap['quiet']:
            print('Virtual environment {0!r} already created, done...'.
                  format(self.env))

        if cmd:
            run_cmd(cmd, echo=not self.bootstrap['quiet'])

        if not self.bootstrap['quiet']:
            print()

    def install_requirements(self):
        """
        Install pip requirements into current environment.
        """
        if not self.bootstrap['quiet']:
            print('== Step 2. Install requirements ==')

        config = self.prepare_config(self.config['pip'])
        args = ' '.join(config_to_args(config))
        cmd = '{0}/bin/pip install {1} -r {2}'.\
              format(self.env, args, self.requirements)

        run_cmd(cmd, echo=not self.bootstrap['quiet'])

        if not self.bootstrap['quiet']:
            print()

    @property
    def is_major(self):
        """
        Returns ``True`` if current virtual environment is major.
        """
        return self.dest is None

    @property
    def is_minor(self):
        """
        Returns ``True`` if current virtual environment is minor.
        """
        return not self.is_major

    def prepare_config(self, config):
        """
        Replace ``{dest}``, ``{env}`` and ``{requirements}`` vars in strings to
        real values.
        """
        config = copy.deepcopy(config)
        environ = dict(copy.deepcopy(os.environ))

        data = {'dest': self.dest,
                'env': self.env,
                'requirements': self.requirements}
        environ.update(data)

        if isinstance(config, string_types):
            config = config.format(**environ)
        else:
            for key, value in iteritems(config):
                if not isinstance(value, string_types):
                    continue
                config[key] = value.format(**environ)

        return config

    def run_hook(self, hook):
        """
        Run necessary post-bootstrap hook.
        """
        if not self.bootstrap['quiet']:
            print('== Step 3. Run post-bootstrap hook ==')

        run_cmd(self.prepare_config(hook),
                echo=not self.bootstrap['quiet'],
                fail_silently=True)

        if not self.bootstrap['quiet']:
            print()


def config_to_args(config):
    """
    Convert config dict to arguments list.
    """
    result = []

    for key, value in iteritems(config):
        if value is False:
            continue

        key = key.replace('_', '-')

        if value is not True:
            result.append('--{0}={1}'.format(key, str(value)))
        else:
            result.append('--{0}'.format(key))

    return result


def error(message, code=None):
    """
    Print error message and exit with error code.
    """
    print('{0}. Exit...'.format(message.rstrip('.')))
    sys.exit(code or 1)


def find_requirements(requirements):
    """
    Split requirements file with last dot and try to find other files in
    current work directory.
    """
    dest = [(None, requirements)]
    filenames = \
        sorted(filter(lambda item: os.path.isfile(item), os.listdir('.')))

    pre, post = requirements.rsplit('.', 1)
    requirements_re = REQUIREMENTS_RE(pre, post)

    for filename in filenames:
        found = requirements_re.findall(filename)

        if not found:
            continue

        dest.append((found[0], filename))

    return dest


def main():
    """
    Initialize argument parser, parse args from command line, find all
    available requirements files, for each that file create environment and
    install all requirements. And finally for main (or only) environment run
    post-bootstrap hook if any.
    """
    if not which('virtualenv'):
        error('``virtualenv`` should be installed in system to continue')

    args = parse_args(sys.argv[1:])

    config = read_config(args.config, args)
    bootstrap = config[__script__]

    if 'virtualenv' in bootstrap['pre_requirements']:
        bootstrap['pre_requirements'].remove('virtualenv')

    for requirement in bootstrap['pre_requirements']:
        if not which(requirement):
            error('Requirement {0!r} is not found in system'.
                  format(requirement))

    if bootstrap['only_major']:
        dest = [(bootstrap['dest'], bootstrap['requirements'])]
    elif not bootstrap['dest']:
        dest = find_requirements(bootstrap['requirements'])
    else:
        dest = [bootstrap['dest']]

    for current in dest:
        env = Environment(current, config)

        env.create()
        env.install_requirements()

        if bootstrap['hook'] and (env.is_major or bootstrap['hook_all']):
            env.run_hook(bootstrap['hook'])

        env.all_ok()


def parse_args(args):
    """
    Parse args from command line by creating argument parser instance and
    process it.
    """
    from argparse import ArgumentParser

    description = 'Bootstrap Python projects with virtualenv and pip.'
    parser = ArgumentParser(description=description)
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument(
        '-c', '--config', default=DEFAULT_CONFIG, dest='config',
        help='Path to config file. By default: {0}'.format(DEFAULT_CONFIG)
    )
    parser.add_argument(
        '-e', '--env', default=DEFAULT_ENV, dest='env',
        help='Name of major virtual environment. By default: {0}'.
             format(DEFAULT_ENV)
    )
    parser.add_argument(
        '-r', '--requirements', default=DEFAULT_REQUIREMENTS,
        dest='requirements',
        help='Path to major requirements file. By default: {0}'.
             format(DEFAULT_REQUIREMENTS))
    parser.add_argument(
        '-p', '--pre-requirements', default=[],
        dest='pre_requirements', nargs='+',
        help='List pre-requirements to check separated by space.'
    )
    parser.add_argument(
        '-C', '--hook', dest='hook', default=None,
        help='Execute this hook after bootstrap process.'
    )
    parser.add_argument(
        '-H', '--hook-all', action='store_true', default=False,
        dest='hook_all',
        help='Execute HOOK in each virtualenv, not only in major one.'
    )

    if which('virtualenv-clone'):
        parser.add_argument(
            '--copy-virtualenv', action='store_true', default=False,
            dest='copy_virtualenv',
            help='Create virtualenv for minor requirements by copying major '
                 'virtualenv. NOTE: If minor venv already exists copy process '
                 'would be aborted to avoid "dest dir exists" error.'
        )

    parser.add_argument(
        '--recreate-virtualenv', action='store_true', default=False,
        dest='recreate_virtualenv',
        help='Recreate virtualenv each time, does not care about exists of '
             'env at disk.'
    )
    parser.add_argument(
        '--only-major', action='store_true', default=False,
        dest='only_major',
        help='Create only major virtual environment, ignore all other '
             'requirements files.'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true', default=False, dest='quiet',
        help='Minimize output, show only error messages.'
    )

    parser.add_argument(
        'dest', default=None, nargs='?',
        help='Bootstrap project using only this minor requirements. By '
             'default major requirements file and all minor files would be '
             'used for bootstrapping.'
    )

    args = parser.parse_args(args)
    args.parser = parser
    return args


def read_config(filename, args):
    """
    Read and parse configuration file. By default, ``filename`` is relative
    path to current work directory.

    If no config file found, default ``CONFIG`` would be used.
    """
    config = {}
    converters = {
        __script__: {
            'pre_requirements': lambda value: value.split(' ')
        }
    }
    default = copy.deepcopy(CONFIG)
    sections = (__script__, 'pip', 'virtualenv')

    if os.path.isfile(filename):
        parser = SafeConfigParser()

        try:
            parser.read(filename)
        except ConfigParserError:
            error('Cannot parse config file at {0!r}'.format(filename))

        for section in sections:
            if not parser.has_section(section):
                continue

            items = parser.items(section)

            if not section in config:
                config[section] = {}

            for key, value in items:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    try:
                        value = bool(strtobool(value))
                    except ValueError:
                        pass

                if section in converters and key in converters[section]:
                    value = converters[section][key](value)

                config[section][key] = value

    for section, data in iteritems(default):
        if section not in config:
            config[section] = data
        else:
            for key, value in iteritems(data):
                if not key in config[section]:
                    config[section][key] = value

    ignore = ('config', 'help', 'version')

    for action in args.parser._actions:
        key = action.dest

        if key in ignore:
            continue

        value = getattr(args, key)

        if action.default == value and key in config[__script__]:
            continue

        config[__script__][key] = value

    return config


def run_cmd(cmd, call=True, echo=False, fail_silently=False):
    """
    Run command with ``subprocess`` module and return output as result.
    """
    if sys.version_info < (2, 7):
        alt_retcode = True
        check_output = subprocess.check_call
    else:
        alt_retcode = False
        check_output = subprocess.check_output

    kwargs = {'shell': True}
    method = subprocess.call if call else check_output
    stdout = sys.stdout if echo else subprocess.PIPE

    if echo:
        print('$ {0}'.format(cmd))

    if call:
        kwargs.update({'stdout': stdout})

    try:
        retcode = method(cmd, **kwargs)
    except subprocess.CalledProcessError as err:
        if fail_silently:
            return False
        error(str(err) if IS_PY3 else unicode(err))

    if call and retcode and not fail_silently:
        error('Command {0!r} returned non-zero exit status {1}'.
              format(cmd, retcode))

    return not retcode if alt_retcode else retcode


def which(executable):
    """
    Shortcut to check whether executable available in current environment or
    not.
    """
    cmd = 'where' if sys.platform.startswith('win') else 'which'
    return run_cmd(' '.join((cmd, executable)), call=False, fail_silently=True)


if __name__ == '__main__':
    main()
