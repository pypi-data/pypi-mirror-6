import argparse
import base64
import getpass
import json
import logging
import os
import pkg_resources
import sys
import urllib2
import argcomplete
from argcomplete.completers import ChoicesCompleter
from prettytable import PrettyTable
from pywizard.resource_set import ResourceSet
import pywizard
import select
from pywizard.books import transform_book_url, Book
from pywizard.registry import PywizardRegistry
from pywizard.utils.cli_controls import cli_password
from pywizard.utils.process import run, RequireSudoException
from pywizard.templating import jinja2_templates
from pywizard.decorators import pywizard_apply
from pywizard.facts import is_ubuntu, is_centos
from pywizard.resources.package_pip import pip_command
from pywizard.utils.execute import check_requirements, __init_agent_logging, pywizard_install_requirements
from pywizard.utils.file_transfer import load_package_from_fs, create_transfer_package, extract_transport_package
from pywizard.worker import worker


def configure_logger(args):
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        level=logging.getLevelName(args.log_level))


def common_init(args):
    configure_logger(args)

    if args.v:
        print 'Pywizard'
        print '-' * 40
        print
        print pip_command('freeze | grep pywizard')
        exit(0)

    if args.agent:
        __init_agent_logging()

    args.path = os.path.abspath(args.path)

    if os.path.isdir(args.path):
        args.path += '/provision.py'

    elif not os.path.exists(args.path):
        sys.stderr.write("\n\n\nfile provision.py do not exist in current directory\n")
        exit(1)

    logging.info('Executing %s' % args.path)

    path = os.path.dirname(args.path)
    if path != '':
        os.chdir(path)

    return path


def package_action(args):
    """
    Handles upload package function, when using with pywizard server
    """

    path = common_init(args)

    provision_pkg = create_transfer_package(path)
    pywizard_pkg = create_transfer_package(os.path.dirname(__file__))

    data = json.dumps({
        'provision': provision_pkg,
        'pywizard': pywizard_pkg,
    })

    # print pywizard_pkg

    with open('package.pkg', 'w+') as f:
        f.write(data)

    logging.info('Package created with len %d kylobytes' % (len(data) / 1024))


def __install_pkg(package, dir_):
    logging.info('Removing old package: %s' % dir_)
    if not os.path.exists(dir_):
        run('mkdir -p %s' % dir_)
    run('rm -rf %s/*' % dir_)
    logging.info('Extracting new package ...')
    extract_transport_package(package, dir_)


def extract_action(args):
    """
    Extracts action
    """

    data = json.load(args.file)

    if 'provision' in data:
        __install_pkg(data['provision'], args.dir)

    if 'pywizard' in data:
        __install_pkg(data['pywizard'], os.path.dirname(pywizard.__file__))


def upload_action(args):
    """
    Handles upload package function, when using with pywizard server
    """

    path = common_init(args)

    if not args.group:
            sys.stderr.write("\n--group attribute should be specified!\n\n")
            exit(1)

    provision_pkg = create_transfer_package(path)
    pywizard_pkg = create_transfer_package(os.path.dirname(__file__))

    data = json.dumps({
        'provision': provision_pkg,
        'pywizard': pywizard_pkg,
    })

    # print pywizard_pkg

    logging.info('Package created with len %d kylobytes' % (len(data) / 1024))

    url = '%s/api/package/%s' % (args.upload, args.group)
    logging.info('Sending package to: %s' % url)
    req = urllib2.Request(url)

    if args.user:
        if not args.password:
            password = getpass.getpass()
        else:
            password = args.password

        base64string = base64.encodestring('%s:%s' % (args.user, password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)

    req.add_header('Content-Type', 'application/json')
    result = urllib2.urlopen(req, data)
    print result.getcode(), result.read()



def apply_action(args):
    """
    Handles pywizard execution
    """

    print '''
        ____       _       __                      __
       / __ \__  _| |     / /_____ ____ __________/ /
      / /_/ / / / | | /| / / /_  // __ `/ ___/ __  /
     / ____/ /_/ /| |/ |/ / / / // /_/ / /  / /_/ /
    /_/    \__, / |__/|__/_/ /___\__,_/_/   \__,_/
          /____/

    '''

    path = common_init(args)

    sys.path.insert(0, path)

    load_os_package_manager()

    with pywizard_apply():
        if args.with_requirements:
            requirements_file = os.path.dirname(args.path) + '/requirements.txt'
            if os.path.exists(requirements_file):
                pywizard_install_requirements(requirements_file)

        if args.roles:
            worker.env.roles += args.roles.split(',')

        if args.config:
            context = open(args.config).read()
        else:
            if args.context:
                context = args.context
            else:
                if select.select([sys.stdin, ], [], [], 0.0)[0]:
                    context = sys.stdin.read().strip()
                else:
                    context = None

        if context:

            ctx = json.loads(context)
            if not 'me' in ctx:
                ctx = {'me': ctx}

            if not 'all' in ctx:
                ctx['all'] = []

            ctx['all'].append(ctx['me'])

            worker.env.context = ctx

            if not args.roles:
                worker.env.roles = worker.env.context['me']['roles']

        jinja2_templates(os.path.dirname(args.path) + '/templates')

        execfile(args.path)

    logging.info('Pywizard execution completed')

    exit(0)


def action_book_list(args):
    # br = PywizardRegistry()
    # print br.list_books().keys()
    tbl = PrettyTable(('Book name', 'ref', 'spells'))

    for entry_point in pkg_resources.iter_entry_points('pywizard.books'):
        parser = argparse.ArgumentParser()
        book = entry_point.load()(Book(parser.add_subparsers()))
        tbl.add_row((entry_point.name, str(entry_point), ', '.join(book.list_spells())))

    print tbl


def action_book_create(args):
    configure_logger(args)

    url = transform_book_url(args.ref)
    print('')
    print('Installing %s' % args.ref)
    print('')
    print('Resolved url: %s' % url)
    print('')
    cmd = pip_command('install %s' % url)

    if args.upgrade:
        cmd += ' --upgrade'

    print(cmd)
    run(cmd)


def action_book_remove(args):
    configure_logger(args)

    url = transform_book_url(args.ref)
    print('')
    print('Installing %s' % args.ref)
    print('')
    print('Resolved url: %s' % url)
    print('')
    cmd = pip_command('uninstall -y %s' % url)
    print(cmd)
    run(cmd)


def action_book_show(args):
    br = PywizardRegistry()
    print br.list_books()[args.book].list_spells().keys()


def action_spell_add(args):
    br = PywizardRegistry()
    if not br.book_exist(args.book):
        br.add_book(args.book)
    br.list_books()[args.book].add_spell(args.name).load_from_file(args.file)
    br.save()


def action_spell_remove(args):
    br = PywizardRegistry()
    br.list_books()[args.book].remove_spell(args.name)
    br.save()


def action_spell_apply(args):

    path = common_init(args)

    load_os_package_manager()

    br = PywizardRegistry()
    br.list_books()[args.book].list_spells()[args.name].apply()


def action_remove_account(args):
    br = PywizardRegistry()
    try:
        br.remove_account(args.type, args.user)
    except KeyError:
        print('No such account!')


def action_show_password(args):
    br = PywizardRegistry()
    try:
        print 'Password: %s' % br.get_account_password(args.type, args.user)
    except KeyError:
        print('No such account!')


def action_add_account(args):
    br = PywizardRegistry()
    br.add_account(args.type, args.user, cli_password())


def action_account_list(args):
    br = PywizardRegistry()

    tbl = PrettyTable(('Type', 'User'))
    if args.type:
        for account in br.list_accounts(args.type):
            tbl.add_row((args.type, account))
    else:
        for type_name in br.list_account_types():
            for account in br.list_accounts(type_name):
                tbl.add_row((type_name, account))

    print tbl


def load_os_package_manager():
    if is_ubuntu():
        import pywizard.resources.package_apt
    if is_centos():
        import pywizard.resources.package_yum

def build_argparser(include_spells=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true', default=False, help='Show version of pywizard and other components')
    parser.add_argument('--log-level', type=str, nargs='?')
    parser.add_argument('--path', nargs='?')
    parser.add_argument('--agent', action='store_true', default=False)
    parser.set_defaults(log_level='DEBUG', path='provision.py')

    subparsers = parser.add_subparsers()

    subpackage = subparsers.add_parser('package', help='Package pywizard scripts')
    subpackage.add_argument('--out', type=argparse.FileType('w+'))
    subpackage.add_argument('--with-pywizard', action='store_true', default=False)
    subpackage.set_defaults(func=package_action)

    # books

    subpackage = subparsers.add_parser('book')
    book_subparsers = subpackage.add_subparsers()

    book_subpackage = book_subparsers.add_parser('install')
    book_subpackage.add_argument('ref', type=str)
    book_subpackage.add_argument('--upgrade', action='store_true', default=False)
    book_subpackage.set_defaults(func=action_book_create)

    book_subpackage = book_subparsers.add_parser('remove')
    book_subpackage.add_argument('ref', type=str)
    book_subpackage.set_defaults(func=action_book_remove)

    book_subpackage = book_subparsers.add_parser('list')
    book_subpackage.set_defaults(func=action_book_list)

    # spells

    spell_main_parser = subparsers.add_parser('spell', help='Apply spell')
    spell_main_parser.add_argument('--rollback', action='store_true', default=False)
    spell_main_parser.set_defaults(use_pywizard_env=True)
    spell_subparsers = spell_main_parser.add_subparsers()

    if include_spells:
        for entry_point in pkg_resources.iter_entry_points('pywizard.books'):
            book = Book(spell_subparsers)
            entry_point.load()(book)

    # accounts

    subpackage = subparsers.add_parser('account-add', help='Create new user account')
    subpackage.add_argument('--type', type=str)
    subpackage.add_argument('user', type=str)
    subpackage.set_defaults(func=action_add_account)

    subpackage = subparsers.add_parser('account-list', help='List accounts')
    subpackage.add_argument('--type', type=str, nargs='?')
    subpackage.set_defaults(func=action_account_list)

    subpackage = subparsers.add_parser('account-remove', help='Remove user account')
    subpackage.add_argument('--type', type=str)
    subpackage.add_argument('user', type=str)
    subpackage.set_defaults(func=action_remove_account)

    subpackage = subparsers.add_parser('account-show', help='Show user account password')
    subpackage.add_argument('--type', type=str)
    subpackage.add_argument('user', type=str)
    subpackage.set_defaults(func=action_show_password)

    subpackage = subparsers.add_parser('extract')
    subpackage.add_argument('--file', type=argparse.FileType('r'))
    subpackage.add_argument('--dir', type=str)
    subpackage.set_defaults(func=extract_action)

    subpackage = subparsers.add_parser('upload')
    subpackage.add_argument('--user', type=str, nargs='?', default=False)
    subpackage.add_argument('--password', type=str, nargs='?', default=False)
    subpackage.add_argument('--group', type=str, nargs='?', default=False)
    subpackage.set_defaults(func=upload_action)

    subpackage = subparsers.add_parser('apply')
    subpackage.add_argument('--roles', type=str, nargs='?')
    subpackage.add_argument('--config', type=str, nargs='?', default=False)
    subpackage.add_argument('--context', type=str, nargs='?')
    subpackage.add_argument('--with-requirements', action='store_true', default=False)
    subpackage.set_defaults(func=apply_action)

    return parser

def pywizard_cmd():
    check_requirements()

    parser = build_argparser(include_spells=True)

    args = parser.parse_args()

    configure_logger(args)

    try:
        if hasattr(args, 'use_pywizard_env'):

            load_os_package_manager()

            worker.resource_set_begin(ResourceSet('main'))
            args.func(args)
            worker.resource_set_end()
            res = worker.resource_set_list[0]

            if args.rollback:
                res.rollback()
            else:
                res.apply()
        else:
            args.func(args)

    except RequireSudoException as e:
        sys.stderr.write('\nCurrent command requires Superuser priveleges.\nReason: %s\n\n' % e.message)
        exit(1)
    except KeyboardInterrupt:
        print('\nInterrupted by user.')
        exit(1)
