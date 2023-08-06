
from pywizard.resources.resource_package import PackageProvider

class YumPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'yum'

    def install_packages(self, packages, version=None):
        import yum
        yb = yum.YumBase()
        for package in packages:
            yb.install(name=package)
        yb.resolveDeps()
        yb.processTransaction()

    def uninstall_packages(self, packages, version=None):
        import yum
        yb = yum.YumBase()
        yb.repos.enableRepo('remi')
        for package in packages:
            yb.remove(name=package)
        yb.resolveDeps()
        yb.processTransaction()

    def get_installed(self, packages):
        import yum
        installed = []
        yb = yum.YumBase()
        yb.conf.cache = True
        pl = yb.doPackageLists()

        for pkg in pl.installed:
            if pkg.name in packages:
                installed.append(pkg.name)

        return set(installed)
