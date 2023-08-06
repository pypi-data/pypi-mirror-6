
from pywizard.resources.resource_package import PackageProvider


class AptPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'apt'

    def install_packages(self, packages, version=None):
        import apt
        cache = apt.Cache()
        for package in packages:
            cache[package].mark_install()

        cache.commit()

    def uninstall_packages(self, packages, version=None):
        import apt
        cache = apt.Cache()
        for package in packages:
            cache[package].mark_delete()

        cache.commit()

    def get_installed(self, packages):
        import apt
        cache = apt.Cache()
        installed = []
        for package in packages:
            if cache[package].is_installed:
                installed.append(package)

        return set(installed)

