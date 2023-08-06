
.. _provision-api:

Provision API
**************************************

File resources
=================

.. automodule:: pywizard.api
   :members: dir, file
   :imported-members:

Both *directory* and *file_* functions return resource as result. And you can use it to
assign event listeners on the resource.

.. currentmodule:: pywizard.resources.file
.. autoclass:: FileResource
    :members: on_create, on_update, on_remove

..
    Packages
    ================

    Python packages
    -------------------

    Pywizard is python, so first thing to know is how to install python packages:

    .. automodule:: pywizard.api
       :members: python_package, python_package_develop
       :imported-members:

    Another important thing is virtualenv support:

    .. automodule:: pywizard.api
       :members: virtualenv
       :imported-members:

    Os packages
    -------------------

    There is a "package" command that can install packages. *package* command relies on PackageProvider to install
    packages. If package provider for your os is installed, then it will be automatically selected.
    To install different packages on different oses you should use :ref:`alternatives-api`.

    .. automodule:: pywizard.api
       :members: package
       :imported-members:

    Both *python_package* and *package* functions return resource as result. And you can use it to
    assign event listeners on the resource.

    .. currentmodule:: pywizard.resources.package
    .. autoclass:: InstallPackageResource
        :members: after_install, before_install


