import os
import sys



class RequireSudoException(Exception):
    pass

def require_sudo(reason='Unknown'):
    if os.getuid() != 0:
        raise RequireSudoException(reason)