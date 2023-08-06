
.. _intro:

Introduction
******************

Pywizard features
===================

- **Zero configuration**
- **Runs locally** on target server
- **Fast**, as there is no ssh in the middle
- Uses **native APIs of linux package managers**, as they are also python
- **Transactional**, first collect resources, show changes needed and then execute if approved
- **It's just python**, so organize your code whatever way you used to


Don't know python can I use pywizard?
=======================================

Yes, you can think about pywizard's scripts as special DSL for provision and you will succeed.

Take a look at this: http://www.stavros.io/tutorials/python/

Or better this: http://docs.python.org/2/tutorial/ (to understand full power of language)

Requirements
================

pythons supported: 2.6, 2.7, 3.3

Installation
===================

Easiest is install using pip::

    $ pip install pywizard

But, may be also installed from source, easily::

    $ python setup.py develop

Hello, world
===================

Here is simple script, that just creates couple files::

    import pywizard.api as pw
    import os

    ctx = pw.context(locals())

    ctx.apply(
        pw.file('/tmp/test1', content='foo1')
    )

Run it using pwizard cli tool, assuming you named it as test.py::

    pywizard apply test.py

You will see changes that need to be applied, and confirmation to apply this changes.

Use-cases
=======================

Addition to package manager
-------------------------------

Pywizard may be used as a tool to install dependencies, that are out if scope of your
package manager pip/npm/packagist.

For this pywizard includes set of batteries (resources):

 - system packages: apt and yum
 - files and directories (files include template support using Jinja2)
 - users
 - services: upstart and sysv
 - shell scripts
 - different config files (ini, yaml, json)
 - git repositories

Pywizard also have mechanism to provide different package/service/etc names for different OS'es. See `alternatives`.

Convention for this is to include provision.py script near to your requirements.txt (in python)

Single server configuration management
----------------------------------------

You can use pywizard from your code to create and clone resources.


