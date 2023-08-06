import apt
from pywizard.compat.os_debian.facts import os_ubuntu

from pywizard.resources.shell import shell

from pywizard.core.env import worker
from pywizard.resources.package import PackageProvider, register_package_provider


class AptPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'apt'

    def can_install_system_packages(self):
        return os_ubuntu()

    def install_packages(self, packages, version=None):
        cache = apt.Cache()
        for package in packages:
            cache[package].mark_install()

        cache.commit()

    def uninstall_packages(self, packages, version=None):
        cache = apt.Cache()
        for package in packages:
            cache[package].mark_delete()

        cache.commit()

    def get_installed(self, packages):

        cache = apt.Cache()
        installed = []
        for package in packages:
            if cache[package].is_installed:
                installed.append(package)

        return set(installed)

#
# def install_libs():
#     shell('apt-get install libapt-pkg-dev')
#     shell('pip install python-apt')
# worker.env.requirements.append(install_libs)

