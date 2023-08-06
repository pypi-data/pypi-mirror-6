from logging import info, debug
import os
from shutil import rmtree
import sys
from pywizard.core.env import worker

from pywizard.core.resource_set import ResourceSet

from pywizard.resources.package import get_package_provider
from pywizard.resources.package_pip import PipPackageProvider
from pywizard.resources.python import python


def env_python_path(home_dir):
    if sys.platform == 'win32':
        python_path = os.path.join(home_dir, 'Scripts', 'python.exe')
    else:
        python_path = os.path.join(home_dir, 'bin', 'python')
    return python_path


def enable_env(home_dir, allow_no_env=False):
        python_path = env_python_path(home_dir)

        if os.path.exists(python_path):
            get_package_provider(PipPackageProvider).push_python(python_path)
        else:
            if allow_no_env:
                debug('Virtual env already do not exist. Using fallback python.')
                # so pop will remove same python
                python_path = get_package_provider(PipPackageProvider).get_python()
                get_package_provider(PipPackageProvider).push_python(python_path)
            else:
                raise Exception('Python executable do not exist in the given env: %s' % python_path)

def reset_env():
    get_package_provider(PipPackageProvider).pop_python()


class WithVirtualenvResourceSet(ResourceSet):

    def __init__(self, home_dir):
        self.home_dir = home_dir
        super(WithVirtualenvResourceSet, self).__init__('Virtualenv %s' % home_dir)

    def before_resource_apply(self, resource):
        enable_env(self.home_dir)

    def after_resource_apply(self, resource):
        reset_env()

    def before_resource_rollback(self, resource):
        enable_env(self.home_dir, True)

    def after_resource_rollback(self, resource):
        reset_env()


class WithVirtualenv(object):

    def __init__(self, home_dir):
        self.home_dir = os.path.realpath(home_dir)

    def __enter__(self):
        worker.resource_set_begin(WithVirtualenvResourceSet(self.home_dir))

    def __exit__(self, exc_type, exc_val, exc_tb):
        worker.resource_set_end()


def virtualenv(home_dir):
    """
    Creates python virtual environment in derictory specified.
    Usual use case is to use this method invocation inside with statement::

        with virtualenv('some/dir'):
            python_package('pywizard')

    So, all python packages that are inside with() context will be installed into given virtual environment.

    :param home_dir: Directory where virtualenv should be created
    :type home_dir: str
    """
    def _apply():
        from virtualenv import create_environment
        create_environment(home_dir)

    def _rollback():
        info('Removing dir %s recursively' % home_dir)
        rmtree(home_dir)

    def env_exist():
        return os.path.exists(env_python_path(home_dir))

    python(_apply, _rollback, if_not=env_exist, description='Create Virtualenv %s' % home_dir)

    return WithVirtualenv(home_dir)


