===========
pywizard
===========

[![Build Status](https://travis-ci.org/pywizard/pywizard.png)](https://travis-ci.org/pywizard/pywizard)


Pywizard is tool that helps you to configure your servers easily.
With Pywizard you describe your server configuration with python-based DSL.
And let pywizard to calculate changes required and apply them to your servers.

Pywizard is mainly for python lovers, as provision(configuration) script is a pure python
So if you are not familiar with python, you should read through at least python tutorial, to use pywizard full power.

Installation is simple ::

    $ pip install pywizard

Tutorial: not yet
Reference manual: a bit later


Some real script example [provision.py]::

    import os
    from pywizard.resources.file import symlink, directory, file_
    from pywizard.resources.package import package

    from pywizard.resources.package_pip import pip_requirements, pip_package
    from pywizard.resources.shell import shell
    from pywizard.resources.user import user
    from pywizard.utils.process import require_sudo, run
    # from pywizard_extra_modules.mysql import mysql_server, mysql_database
    from pywizard.templating import tpl
    from modules.mysql import mysql_database
    from pywizard.resources.service import service
    from modules.utils import git_clone, elasticsearch

    require_sudo()

    package([
        'vim',
        'htop',

        'python',
        'python-dev',
        'git',
        'python-pip',

        'libjpeg-dev',
        'libfreetype6',
        'libfreetype6-dev',
        'zlib1g-dev',
        'libmemcached-dev',
        'libmysqld-dev',

        'mysql-server',

        'memcached',

        'gunicorn',
        'nginx'
    ])

    symlink('/usr/lib/x86_64-linux-gnu/libjpeg.so', '/usr/lib/libjpeg.so')
    symlink('/usr/lib/x86_64-linux-gnu/libfreetype.so', '/usr/lib/libfreetype.so')
    symlink('/usr/lib/x86_64-linux-gnu/libz.so', '/usr/lib/libz.so')

    git_clone('git@bitbucket.org:ribozz/awesomebit.git', '/var/src/awesomebit')


    # pip_package('distribute>=0.6.28')

    pip_requirements('/var/src/awesomebit/maxe/core/requirements.txt')


    deployments = [
        {
            'name': 'inter24',
            'domain': 'inter24.se',
            'app_port': 6501
        }
    ]

    elasticsearch('0.90.0')

    for deployment in deployments:
        user_name = deployment['name']
        user(user_name)
        deployment_home = '/home/deployments/%s' % user_name
        directory(deployment_home)

        file_('/etc/init/%s_gunicorn.conf' % user_name, content=tpl('gunicorn.conf', {
            'home': deployment_home,
            'user': user_name,
            'port': deployment['app_port']
        }))

        file_('/etc/nginx/sites-enabled/%s.conf' % user_name, content=tpl('nginx.conf', {
            'home': deployment_home,
            'id': user_name,
            'domain': deployment['domain'],
            'ssl': False,
            'port': deployment['app_port']
        }))

        mysql_database(user_name, '123123', user_name)
        service('nginx')
        service('%s_gunicorn' % user_name, controller='upstart')


