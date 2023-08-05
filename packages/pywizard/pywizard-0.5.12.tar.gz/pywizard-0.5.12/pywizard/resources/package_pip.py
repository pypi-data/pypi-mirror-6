import re
from pywizard.facts import is_ubuntu
from pywizard.resources.shell import shell
from pywizard.resources.package import PackageProvider, register_package_provider, package
from pywizard.utils.process import run


def  pip_command(command):
    pip = 'pip-python'

    if is_ubuntu():
        pip = 'pip'
    return '%s %s' % (pip, command)


class PipPackageProvider(PackageProvider):

    @staticmethod
    def get_key():
        return 'pip'

    def install_packages(self, packages, version=None):
        run(pip_command('install %s' % ' '.join(packages)), log_output=True)

    def uninstall_packages(self, packages, version=None):

        run(pip_command('uninstall -y -q %s' % ' '.join(packages)), log_output=True)

    def get_installed(self, packages):
        packages = [re.split('(>|=|<){2}', x)[0] for x in packages]
        status = run(pip_command("freeze 2>&1 | grep -P \"^(%s)==\"" % '|'.join(packages)), ignore_errors=True)
        status = status.split('\n')
        installed = []
        for line in status:
            if not len(line.strip()):
                continue
            package, version = line.split('==')
            installed.append(package)

        return set(installed)

register_package_provider(PipPackageProvider)


def pip_requirements(filename):
    shell(pip_command('install --use-mirrors -r %s' % filename))


def pip_package(packages):
    package(packages, required_provider=PipPackageProvider)
