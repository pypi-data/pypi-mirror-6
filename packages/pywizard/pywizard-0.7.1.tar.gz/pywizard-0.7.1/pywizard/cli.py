import argparse
import logging
import re
import os
import sys
from tempfile import mkstemp
from pywizard.context import Context
from pywizard.resources.sudo import RequireSudoException
import pywizard.api as pw

# allow monkey-patching on test
try:
    _raw_input = raw_input
except NameError:
    _raw_input = input

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


def execute(path, ctx):
    sys.path.insert(0, os.path.dirname(path))
    exec(compile(open(path).read(), path, 'exec'), globals(), locals())


def yn_choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = _raw_input("%s (%s) " % (message, choices))
    values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
    return choice.strip().lower() in values


def apply_action(args):
    """
    Handles pywizard execution
    """

    path = args.path

    context = Context()

    with pw.resource_set(context, name='main', rollback=args.rollback):
        execute(path, context)

    if args.tree:
        more_indent = re.compile(r'^(\s*)', re.MULTILINE)
        print(more_indent.sub(r'\1\1\1', context.to_xml().prettify()))

    changes = context.changeset()

    if changes.needed():
        if not args.force:
            print('\nChanges to be applied:\n')
            for item in changes.items:
                print('\t - %s' % item.description)

        if not args.dry:
            if args.force or yn_choice('\nApply?', default='n'):
                changes.commit()

                print('\nChanges has been successfully applied.\n')

            else:
                print('\nNo changes has been made.\n')

    else:
        print('\nNo changes needed.\n')

    logging.info('Pywizard execution completed')


def build_argparser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subpackage = subparsers.add_parser('apply', help='Execute provision script, collect all resources and apply them.')
    subpackage.add_argument('path', help='Specify path to provision script. provision.py in current'
                                                 'directory by default. Also may include url.', default='provision.py')
    subpackage.add_argument('-r', '--rollback', action='store_true', default=False, help='If specified will rollback all'
                                                                                   'resources applied.')
    subpackage.add_argument('--tree', action='store_true', default=False, help='Print resource tree')
    subpackage.add_argument('--dry', action='store_true', default=False, help='Just print changes list')
    subpackage.add_argument('--force', action='store_true', default=False, help='Apply without confirmation')

    subpackage.set_defaults(func=apply_action)

    return parser


def pywizard_cmd(args=None):

    if args is None:
        print('''
        ____       _       __                      __
       / __ \__  _| |     / /_____ ____ __________/ /
      / /_/ / / / | | /| / / /_  // __ `/ ___/ __  /
     / ____/ /_/ /| |/ |/ / / / // /_/ / /  / /_/ /
    /_/    \__, / |__/|__/_/ /___\__,_/_/   \__,_/
          /____/

    ''')
        args = sys.argv[1:]

    parser = build_argparser()

    if not args:
        parser.print_usage()
        print('\n')

        exit(1)
    else:
        args = parser.parse_args(args=args)

        try:
            args.func(args)

        except RequireSudoException as e:
            sys.stderr.write('\nCurrent command requires Superuser priveleges.\nReason: %s\n\n' % e.message)
            exit(1)
        except KeyboardInterrupt:
            print('\nInterrupted by user.')
            exit(1)
