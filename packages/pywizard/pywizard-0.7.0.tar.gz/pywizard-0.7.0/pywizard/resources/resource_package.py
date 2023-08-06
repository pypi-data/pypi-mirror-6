"""
Resource for package management
"""

from logging import info, error, debug
from pywizard.resource import Resource
from pywizard.events import event, event_property


class PackageProvider(object):

    """
    Base class for package providers
    """

    # static

    _providers = {}

    __default = None

    @staticmethod
    def get_key():
        """
        Short name that will be used as a part of resource key
        @return: string
        """

    @staticmethod
    def set_default(provider):
        PackageProvider.__default = provider

    @staticmethod
    def get_default():
        if not PackageProvider.__default:
            if len(PackageProvider._providers):
                for _provider in PackageProvider._providers.values():
                    if _provider.can_install_system_packages():
                        PackageProvider.__default = _provider
                        return _provider
            else:
                raise Exception('No system package providers installed!')

        return PackageProvider.__default


    @staticmethod
    def get_key():
        """
        Short name that will be used as a part of resource key
        @return: string
        """

    def can_install_system_packages(self):
        """
        Short name that will be used as a part of resource key
        @return: string
        """
        return False

    def on_package_registered(self, package_resource):
        """
        Short name that will be used as a part of resource key
        @return: string
        """
        return False

    def install_packages(self, packages, version=None):
        """
        Install package.
        name may be also a list containing several package names

        @param version: optional version as string (if package provider supports this)
        @param packages: list of packages or single package as string
        """
        pass

    def uninstall_packages(self, packages, version=None):
        """
        Uninstall package.
        name may be also a list containing several package names

        @param version: optional version as string (if package provider supports this)
        @param packages: list of packages or single package as string
        """
        pass

    def get_installed(self, packages):
        """
        Method should check each package from the list given and
        return names of installed packages (filter out not installed)

        @param packages: list of strings
        """
        return ()

    def get_not_installed(self, packages):
        """
        Accepts list of packages and return only not installed from this list.

        @param packages: list of strings
        """
        return set(packages) - self.get_installed(packages)

    def is_installed(self, package_name):
        """
        Check if package is installed

        @param package_name:
        @return:
        """
        return len(self.get_installed(package_name)) > 0


def register_package_provider(provider):
    assert issubclass(provider, PackageProvider)
    PackageProvider._providers[provider.get_key()] = provider()

def get_package_provider(provider):
    assert issubclass(provider, PackageProvider)
    return PackageProvider._providers[provider.get_key()]


class InstallPackageResource(Resource):
    packages = ''
    package_provider = None

    after_install = event_property('after_install', 'Executed after package installation')
    before_install = event_property('before_install', 'Executed after package removal')

    def __init__(self, packages, provider):
        if isinstance(packages, str):
            packages = (packages,)

        self.packages = packages
        self.package_provider = provider

    def get_resource_keys(self):
        return ['package:%s:%s' % (self.package_provider.get_key(), package) for package in self.packages]

    def resolve_conflict(self, resource):
        """
        If package has equal keys, then they are equal (currently at least)

        @param resource:
        @return:
        """
        pass

    def apply(self):

        provider = self.package_provider

        packs_to_install = provider.get_not_installed(set(self.packages))

        if len(packs_to_install) > 0:
            info("Installing packages %s" % packs_to_install)

            event(self.before_install)

            provider.install_packages(packs_to_install)

            not_installed_packs = provider.get_not_installed(packs_to_install)
            if len(not_installed_packs) > 0:
                error('The following packages was not installed on some reason: %s' % not_installed_packs)
            else:
                event(self.after_install)
                info('All packages installed: %s' % packs_to_install)
        else:
            debug('All packages already installed')

    def rollback(self):

        provider = self.package_provider

        packs_to_uninstall = provider.get_installed(set(self.packages))

        if len(packs_to_uninstall) > 0:
            info("Uninstalling packages %s" % packs_to_uninstall)
            provider.uninstall_packages(packs_to_uninstall)

            still_installed_packs = provider.get_installed(packs_to_uninstall)
            if len(still_installed_packs) > 0:
                error('The following packages was not removed on some reason: %s' % still_installed_packs)
            else:
                info('All packages removed: %s' % packs_to_uninstall)
        else:
            debug('No packages to uninstall')

    def describe(self):
        return "Packages: %s" % ['%s:%s' % (self.package_provider.get_key(), pack) for pack in self.packages]


def package(packages, required_provider=None):
    """
    Installs package.
    """

    if required_provider is None:
        provider = PackageProvider.get_default()
    else:
        assert issubclass(required_provider, PackageProvider)
        provider = PackageProvider._providers[required_provider.get_key()]

    if not isinstance(provider, PackageProvider):
        raise Exception('No required package provider installed: %s' % (required_provider or 'system package provider'))

    return InstallPackageResource(packages, provider)


