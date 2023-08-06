import argparse
import logging
import os
import sys
from tempfile import mkstemp
from lxml import etree
from pywizard.context import Context
from pywizard.resources.sudo import RequireSudoException
import pywizard.api as pw

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


def configure_logger(args):
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        level=logging.getLevelName(args.log_level))

def common_init(args):
    configure_logger(args)


def execute(path, ctx):
    if os.path.exists(path):
        sys.path.insert(0, os.path.dirname(path))
        exec(compile(open(path).read(), path, 'exec'), globals(), locals())
    else:
        f = urlopen(path)
        handle, fileaname = mkstemp()

        with open(fileaname, 'w+') as tmp:
            tmp.write(f.read())

        f.close()

        exec(compile(open(fileaname).read(), fileaname, 'exec'), globals(), locals())

        os.remove(fileaname)

def yn_choice(message, default='y'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("%s (%s) " % (message, choices))
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
        print(etree.tostring(context.to_xml(), pretty_print=True))

    changes = context.changeset()

    if not args.force:
        print('\n')
        for item in changes.items:
            print('\t - %s' % item)

    if not args.dry:
        if args.force or yn_choice('Apply changes?'):
            changes.commit()

    logging.info('Pywizard execution completed')


def build_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', type=str, help='Log level. Useful ones: DEBUG, INFO, ERROR',
                        default='INFO')
    parser.add_argument('-v', action='store_const', dest='log-level', const='DEBUG', help='Set log level to debug',
                        default='INFO')

    subparsers = parser.add_subparsers()

    subpackage = subparsers.add_parser('apply', help='Execute provision script, collect all resources and apply them.')
    subpackage.add_argument('path', help='Specify path to provision script. provision.py in current'
                                                 'directory by default. Also may include url.', default='provision.py')
    subpackage.add_argument('--rollback', action='store_true', default=False, help='If specified will rollback all'
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
        args = sys.argv

    args = build_argparser().parse_args(args=args)

    configure_logger(args)

    try:


        args.func(args)

    except RequireSudoException as e:
        sys.stderr.write('\nCurrent command requires Superuser priveleges.\nReason: %s\n\n' % e.message)
        exit(1)
    except KeyboardInterrupt:
        print('\nInterrupted by user.')
        exit(1)
