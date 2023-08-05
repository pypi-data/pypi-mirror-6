"""

"""
from getpass import getpass
from random import choice
import re
import string


def cli_select(items, prompt='Select variant: ', ret_number=False):
    while True:
        print('\nSelect one of items:\n')
        for i, item in enumerate(items):
            print '\t%d) %s' % (i, item)
        ret = raw_input('\n%s' % prompt)

        if not ret.isdigit():
            print '\nEnter number, please!'
            continue

        nr = int(ret)
        if nr < 0 or nr >= len(items):
            print '\nPlease, enter digit %d-%d!' % (0, len(items) - 1)
            continue

        if ret_number:
            return nr
        return items[nr]


def cli_text(prompt='Enter text:', pattern='.+', error_text=None, default=None):
    while True:

        if default:
            prompt += ' (blank for default: %s)' % default

        ret = raw_input('\n%s' % prompt)

        if ret == '' and default:
            return default

        if not re.match(pattern, ret):
            if not error_text:
                print '\nText should match pattern: %s' % pattern
            else:
                print '\n%s' % error_text
            continue

        return ret

def cli_confirm(prompt):
    return cli_text('\n%s (y/n):' % prompt, '^[yn]$', 'Enter y or n')


def cli_password(prompt='Enter password:', len_minimum=5, len_recommended=12, chars=None):

    while True:
        password1 = getpass('\n%s (leave empty to auto-generate)' % prompt)

        if password1 == '':
            # generate password
            if not chars:
                chars = string.ascii_letters + string.digits + '!@#$%^&*()'
            return ''.join([choice(chars) for i in range(len_recommended)])

        if len(password1) < len_minimum:
            print '\nPassword should be longer than %d symbols' % len_minimum
            continue

        password2 = getpass('\nConfirm password:')

        if password1 != password2:
            print '\nPasswords do not match.'
            continue

        return password1





