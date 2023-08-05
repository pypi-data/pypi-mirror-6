import re
from pywizard.resources.package import PackageProvider, register_package_provider, package
from pywizard.utils.process import run
import yum


def yum_command(command):
    return '%s %s' % ('yum', command)


class YumPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'yum'

    def can_install_system_packages(self):
        return True

    def install_packages(self, packages, version=None):
        yb = yum.YumBase()
        for package in packages:
            yb.install(name=package)
        yb.resolveDeps()
        yb.processTransaction()

    def uninstall_packages(self, packages, version=None):
        yb = yum.YumBase()
        yb.repos.enableRepo('remi')
        for package in packages:
            yb.remove(name=package)
        yb.resolveDeps()
        yb.processTransaction()

    def get_installed(self, packages):
        installed = []
        yb = yum.YumBase()
        yb.conf.cache = True
        pl = yb.doPackageLists()

        for pkg in pl.installed:
            if pkg.name in packages:
                installed.append(pkg.name)

        return set(installed)

register_package_provider(YumPackageProvider)
