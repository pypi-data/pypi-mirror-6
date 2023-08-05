import os
from os.path import expanduser
import pickle
from pywizard.books import Book

__author__ = 'alex'


class PywizardRegistry(object):
    path = None
    data = None

    def __init__(self):
        self.data = {}
        self.path = expanduser('~')

        self.load()

    def is_empty(self):
        return True

    def clear(self):
        self.data = {}
        self.save()

    def save(self):
        with open(self._get_file_name(), 'wb') as f:
            pickle.dump(self.data, f)

    def _get_file_name(self):
        return self.path + os.path.sep + '.pywizard'

    def load(self):

        self.data = {}

        fname = self._get_file_name()
        if os.path.exists(fname):
            with open(self._get_file_name(), 'r') as f:
                try:
                    self.data = pickle.load(f)
                except EOFError:
                    pass

    def reload(self):
        self.load()

    def list_books(self):
        if not '_books' in self.data:
            self.data['_books'] = {}
        return self.data['_books']

    def add_book(self, book_name):
        self.list_books()[book_name] = Book()
        self.save()

    def remove_book(self, book_name):
        del self.list_books()[book_name]
        self.save()

    def book_exist(self, name):
        return name in self.list_books()

    def list_account_types(self):
        if not '_accounts' in self.data:
            self.data['_accounts'] = {}
        return self.data['_accounts'].keys()

    def add_account(self, type_name, user, password):
        if not '_accounts' in self.data:
            self.data['_accounts'] = {}
        if not type_name in self.data['_accounts']:
            self.data['_accounts'][type_name] = {}

        self.data['_accounts'][type_name][user] = password
        self.save()
        return self.data['_accounts'][type_name][user]

    def list_accounts(self, type_name):
        if not '_accounts' in self.data:
            return {}
        if not type_name in self.data['_accounts']:
            return {}

        return self.data['_accounts'][type_name]

    def get_account_password(self, type_name, user):
        return self.list_accounts(type_name)[user]

    def update_account_password(self, type_name, user, password):
        # may change in future, so we need to have own method for password update
        self.add_account(type_name, user, password)
        self.save()

    def _properties(self):
        if not '_properties' in self.data:
            self.data['_properties'] = {}
        return self.data['_properties']

    def remove_account(self, type_name, user):
        del self.data['_accounts'][type_name][user]
        if len(self.data['_accounts'][type_name]) == 0:
            del self.data['_accounts'][type_name]
        self.save()

    def set_property(self, name, value):
        self._properties()[name] = value
        self.save()

    def has_property(self, name):
        return name in self._properties()

    def get_property(self, name):
        if not self.has_property(name):
            return None
        return self._properties()[name]

    def remove_property(self, name):
        if self.has_property(name):
            del self._properties()[name]
            self.save()


