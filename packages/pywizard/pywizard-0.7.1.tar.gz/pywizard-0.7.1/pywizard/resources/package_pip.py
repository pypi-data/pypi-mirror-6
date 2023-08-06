from collections import deque
from logging import debug
import subprocess
import sys

import os
from pywizard.process import process_run
from pywizard.resources.resource_package import PackageProvider, register_package_provider, package, get_package_provider
from pywizard.resources.resource_python import python


class PipPackageProvider(PackageProvider):
    def __init__(self):
        super(PipPackageProvider, self).__init__()

        self.pythons = deque()
        self.push_python(sys.executable)

    def get_python(self):
        return self.pythons[-1]

    def get_pip(self):
        return os.path.join(os.path.dirname(self.get_python()), 'pip')

    def push_python(self, path):
        debug('Python is set to: %s' % path)
        self.pythons.append(path)

    def pop_python(self):
        self.pythons.pop()
        debug('Python is back to: %s' % self.get_python())


    @staticmethod
    def get_key():
        return 'pip'

    def install_packages(self, packages, version=None):
        process_run([self.get_pip(), 'install', '--upgrade'] + list(packages))

    def uninstall_packages(self, packages, version=None):
        process_run([self.get_pip(), 'uninstall', '-y', '-q'] + list(packages))

    def get_installed(self, packages):
        command = [self.get_python(), os.path.dirname(__file__) + os.path.sep + '_util_package_pip_.py']
        proc = subprocess.Popen(command, shell=False,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        proc.stdin.write('\n'.join(packages).encode('ascii', 'ignore'))
        proc.stdin.close()

        proc.wait()

        if proc.returncode != 0:
            raise Exception('Error when executing ' + str(command) + '\n'.join(proc.stderr.readlines())
                            + '\n'.join(proc.stdout.readlines()) + ' Exit code: ' + str(proc.returncode))

        l = proc.stdout.read()
        if l.strip() == '':
            return set()
        else:
            return set(l.decode('ascii').split('\n'))


register_package_provider(PipPackageProvider)


def env_python():
    return get_package_provider(PipPackageProvider).get_python()


def pip_requirements(filename):
    def _apply():
        run([env_python(), 'install', '-r', filename])

    python(_apply)


def python_package_develop(dir):
    """
    Installs python package as development requirement.
    Takes virtual environment into account, if given.
    """
    _dir = os.path.realpath(dir)

    def _apply():
        run([env_python(), _dir + os.path.sep + 'setup.py', 'develop'], log_output=False)

    python(_apply, description='Installing %s as development package.' % _dir)


def pip_package(*packages):
    """
    Install python packages.
    Takes virtual environment into account, if given.
    """
    return package(packages, required_provider=PipPackageProvider)


