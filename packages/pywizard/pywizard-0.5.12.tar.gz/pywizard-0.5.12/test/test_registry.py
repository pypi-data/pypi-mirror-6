from os.path import expanduser
import pytest
from pywizard.books import Book
from pywizard.registry import PywizardRegistry

__author__ = 'alex'


def test_register():
    book_registry = PywizardRegistry()
    assert book_registry.is_empty()
    assert book_registry.path == expanduser('~')


def test_persist_property():
    br = PywizardRegistry()
    br.data['boo'] = 123
    br.save()

    # another registry should read data from same place
    another = PywizardRegistry()
    assert another.data['boo'] == 123

    # clear oner registry mean we clean every
    another.clear()

    with pytest.raises(KeyError):
        assert another.data['boo'] == 123

    # but, old will have old data
    assert br.data['boo'] == 123

    # untill refresh
    br.reload()

    with pytest.raises(KeyError):
        assert br.data['boo'] == None


def test_book_list():
    br = PywizardRegistry()
    assert len(br.list_books()) == 0

    br.add_book('foo')

    assert len(br.list_books()) == 1
    assert isinstance(br.list_books()['foo'], Book)

    br.remove_book('foo')

    assert len(br.list_books()) == 0


def test_books_are_persisted():
    br = PywizardRegistry()
    br.clear()

    assert not br.book_exist('foo')

    assert len(br.list_books()) == 0
    br.add_book('foo')
    assert len(br.list_books()) == 1

    assert br.book_exist('foo')

    br2 = PywizardRegistry()
    assert len(br2.list_books()) == 1
    br2.clear()

    br3 = PywizardRegistry()
    assert len(br2.list_books()) == 0


def test_accounts():
    br = PywizardRegistry()
    br.clear()

    assert len(br.list_account_types()) == 0
    assert len(br.list_accounts('foo')) == 0
    assert len(br.list_accounts('bar')) == 0

    br.add_account(type_name='foo', user='user1', password='123')

    assert br.list_account_types() == ['foo']
    assert len(br.list_accounts('foo')) == 1
    assert len(br.list_accounts('bar')) == 0

    assert br.get_account_password('foo', 'user1') == '123'
    br.update_account_password('foo', 'user1', '124')
    assert br.get_account_password('foo', 'user1') == '124'

    br.remove_account('foo', 'user1')

    assert len(br.list_account_types()) == 0
    assert len(br.list_accounts('foo')) == 0
    assert len(br.list_accounts('bar')) == 0


def test_attributes():
    br = PywizardRegistry()

    assert not br.has_property('foo')
    assert br.get_property('foo') is None

    br.set_property('foo', 123)

    assert br.has_property('foo')

    assert br.get_property('foo') == 123

    br.remove_property('foo')

    assert not br.has_property('foo')
    assert br.get_property('foo') is None








