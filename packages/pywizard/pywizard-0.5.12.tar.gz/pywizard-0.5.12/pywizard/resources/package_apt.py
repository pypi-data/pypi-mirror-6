
from pywizard.resources.package import PackageProvider, register_package_provider, package
import apt
from pywizard.resources.shell import shell
from pywizard.worker import worker


class AptPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'apt'

    def can_install_system_packages(self):
        return True

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


def install_libs():
    shell('apt-get install libapt-pkg-dev')
    shell('pip install python-apt')
worker.env.requirements.append(install_libs)

register_package_provider(AptPackageProvider)