"""

"""
from pywizard.registry import PywizardRegistry
from pywizard.utils.cli_controls import cli_text, cli_password, cli_select


def _create_user(br, type_name, purpose, user=None):
    if not user:
        user = cli_text('Enter username for %s (%s): ' % (purpose, type_name), '^\S{3,}$')
    password = cli_password('Set password fo user %s' % user)
    br.add_account(type_name, user, password)
    return user, password


def get_account(type_name, purpose):
    """
    Retreives account of given type for purpose given.

    :param type_name: Name of account type. Ex 'mysql'
    :type type_name: string
    :param purpose: Describe how this password will be used (one short sentence, couple words)
    :param user:
    :type user: string
    :rtype: tuple
    :return: account username and account password as tuple of two elements
    """

    br = PywizardRegistry()
    accounts = br.list_accounts(type_name)

    if not accounts:
        return _create_user(br, type_name, purpose)

    else:
        select = cli_select(['Create new user'] + accounts.keys(), 'Select user to use for %s (%s)' % (purpose, type_name), ret_number=True)
        if select == 0:
            return _create_user(br, type_name, purpose)
        else:
            user = accounts.keys()[select - 1]
            return user, accounts[user]


def get_password_for_user(type_name, user, purpose='Unknown'):
    """
    @param type_name:
    @param purpose: Describe how this password will be used (one short sentence, couple words)
    @param user:
    @return:
    """

    br = PywizardRegistry()
    accounts = br.list_accounts(type_name)

    if not accounts or not user in accounts:
        return _create_user(br, type_name, purpose, user)
    else:
        return accounts[user]


def get_attribute(name, purpose, default=None, pattern='.*'):
    """
    Retrieves attribute from pywizard database.
    """

    br = PywizardRegistry()

    if br.has_property(name):
        return br.get_property(name)
    else:
        value = cli_text('Enter %s' % purpose, pattern, default=default)
        br.set_property(name, value)
        return value

