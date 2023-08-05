"""

"""
import os
from os.path import expanduser
import pickle
import re
from urlparse import urlparse
from pywizard.worker import ResourceSet
from pywizard.worker import worker


class UnknownBookUrlScheme(Exception):
    pass


def transform_book_url(url):
    if not re.match('^\w+://', url):
        url = 'github://' + url

    parts = urlparse(url, allow_fragments=True)

    scheme = parts.scheme
    host = parts.hostname
    path = parts.path
    tag = parts.fragment

    if parts.username:
        path = 'pywizard-book-' + host
        host = parts.username

    if path == '':
        path = host
        host = 'pywizard'

    if path[0] == '/':
        path = path[1:]

    if not scheme in ('github',):
        raise UnknownBookUrlScheme(scheme)

    if scheme == 'github':
        if tag:
            template = 'git+https://github.com/%(user)s/%(repo)s.git@%(commit)s#egg=%(repo)s'
        else:
            template = 'git+https://github.com/%(user)s/%(repo)s.git#egg=%(repo)s'

        return template % {
            'user': host,
            'repo': path,
            'commit': tag,
        }


class Book(object):

    spells = None
    source_url = None
    resolved_url = None

    def __init__(self, cli_parser):
        self.parser = cli_parser
        self.spells = []
        super(Book, self).__init__()

    def list_spells(self):
        return self.spells

    def add_spell(self, spell_name):
        self.spells.append(spell_name)
        return self.parser.add_parser(spell_name)

    def remove_spell(self, spell_name):
        del self.spells[spell_name]


def _exec_from_file(instance):
    execfile(instance.filename)


class Spell(object):
    func = None
    filename = None

    def set_func(self, func):
        self.func = func

    def collect_resources(self):
        worker.resource_set_begin(ResourceSet('main'))
        self.func(self)
        worker.resource_set_end()

        return worker.resource_set_list

    def apply(self):
        self.collect_resources()[0].apply()

    def load_from_file(self, filename):
        self.filename = filename
        self.func = _exec_from_file

