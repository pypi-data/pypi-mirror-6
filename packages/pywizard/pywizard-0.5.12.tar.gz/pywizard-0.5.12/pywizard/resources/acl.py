from pywizard.resources.shell import shell


def setfacl(directory, username, rights, recursive=False):
    command = 'setfacl -m u:%s:%s'
    if recursive:
        command += ' -R'
    shell(command % (username, rights, directory))


