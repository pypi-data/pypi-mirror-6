from pkg_resources import Requirement
import pkg_resources
import sys

if __name__ == "__main__":

    installed = []
    for pkg in sys.stdin.readlines():
        pkg = pkg.strip()
        if len(pkg):

            req = Requirement.parse(pkg)
            try:
                found = pkg_resources.working_set.find(req)
                if found:
                    installed.append(pkg)
            except pkg_resources.VersionConflict:
                pass
    sys.stdout.write('\n'.join(installed))
    exit(0)