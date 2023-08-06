

# resources
from pywizard.resources.resource_file import file_ as file, directory as dir, replace_in_file

from pywizard.resource import resource_set
from pywizard.context import context

# from pywizard.resources.resource_python import python
from pywizard.resources.resource_package import package
from pywizard.resources.package_pip import pip_package

# from pywizard.resources.resource_virtualenv import virtualenv
# from pywizard.resources.package_pip import python_package, python_package_develop
from pywizard.alternatives import one_of, all_of
from pywizard.templating import jinja
