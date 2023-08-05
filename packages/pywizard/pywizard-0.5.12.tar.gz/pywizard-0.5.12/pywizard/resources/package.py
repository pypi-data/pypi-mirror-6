"""
Resource for package management
"""

import inspect
from logging import info, error, debug
from pywizard.utils.process import run
from pywizard.resource import Resource
from pywizard.utils.events import event
from pywizard.worker import worker


class PackageProvider(object):

    """
    Base class for package providers
    """

    # static

    _providers = {}

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


class InstallPackageResource(Resource):
    packages = ''
    package_provider = None
    before_install = None

    def __init__(self, packages, provider, before_install=None, after_install=None):
        if isinstance(packages, str):
            packages = (packages,)

        self.packages = packages
        self.package_provider = provider
        self.before_install = before_install
        self.after_install = after_install

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


def package(packages, required_provider=None, before_install=None, after_install=None):

    provider = None
    if required_provider is None:
        if len(PackageProvider._providers):
            for _provider in PackageProvider._providers.itervalues():
                if _provider.can_install_system_packages():
                    provider = _provider
        else:
            raise Exception('No system package providers installed!')
    else:
        assert issubclass(required_provider, PackageProvider)
        provider = PackageProvider._providers[required_provider.get_key()]

    if not isinstance(provider, PackageProvider):
        raise Exception('No required package provider installed: %s' % (required_provider or 'system package provider'))

    worker.register_resource(
        InstallPackageResource(packages, provider, before_install, after_install)
    )


