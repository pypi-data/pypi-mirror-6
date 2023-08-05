"""

"""
import os
from os.path import expanduser
from pywizard.resources.python import PythonResource
from pywizard.worker import worker as _worker
import pytest
from pywizard.resources.file import directory
from pywizard.registry import PywizardRegistry
from pywizard.books import Book, Spell, UnknownBookUrlScheme, transform_book_url

tmp_dir = os.path.realpath(__file__) + os.path.sep + '_tmp'

@pytest.fixture
def worker():
    _worker.reset()
    return _worker


def test_book():

    book = Book()
    
    assert len(book.list_spells()) == 0

    ret = book.add_spell('foo')

    assert isinstance(ret, Spell) # should return the spell created

    assert len(book.list_spells()) == 1
    assert isinstance(book.list_spells()['foo'], Spell)

    book.remove_spell('foo')

    assert len(book.list_spells()) == 0


def test_spell(worker):

    def resource_func():
        resource_func.is_called = True
    resource_func.is_called = False

    def buga_buga(instance):
        buga_buga.is_called = True
        worker.register_resource(
            PythonResource(
                resource_func,
                description='Replace in file'
            )
        )

    buga_buga.is_called = False

    spell = Spell()
    spell.set_func(buga_buga)

    assert not buga_buga.is_called

    resources = spell.collect_resources()

    assert buga_buga.is_called

    assert len(resources) > 0

    resources[0].apply()

    assert resource_func.is_called

    resource_func.is_called = False

    worker.reset()

    spell.apply()

    assert resource_func.is_called


def test_spell_with_file():

    spell = Spell()
    spell.load_from_file('/tmp/foo/bar')

    assert spell.filename == '/tmp/foo/bar'

def test_url_scheme_resolver_unknown_scheme():
    with pytest.raises(UnknownBookUrlScheme):
        transform_book_url('boo://bodsfksjl')


@pytest.mark.parametrize(("given", "expected"), [
    (
        "github://tangentlabs/django-oscar#d636b803d98cd1d3edd01821d4fb2a01ce215ee4",
        "git+https://github.com/tangentlabs/django-oscar.git@d636b803d98cd1d3edd01821d4fb2a01ce215ee4#egg=django-oscar"
    ),
    (
        "tangentlabs/django-oscar#d636b803d98cd1d3edd01821d4fb2a01ce215ee4",
        "git+https://github.com/tangentlabs/django-oscar.git@d636b803d98cd1d3edd01821d4fb2a01ce215ee4#egg=django-oscar"
    ),
    (
        "tangentlabs/django-oscar",
        "git+https://github.com/tangentlabs/django-oscar.git#egg=django-oscar"
    ),
    (
        "django-oscar",
        "git+https://github.com/pywizard/django-oscar.git#egg=django-oscar"
    ),
    (
        "ribozz@django-oscar",
        "git+https://github.com/ribozz/pywizard-book-django-oscar.git#egg=pywizard-book-django-oscar"
    ),
])
def test_url_scheme_resolver(given, expected):
    assert transform_book_url(given) == expected

