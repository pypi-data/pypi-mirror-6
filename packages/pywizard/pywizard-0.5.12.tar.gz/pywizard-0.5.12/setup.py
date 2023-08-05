import os
from setuptools import setup
# from tests import PyTest

setup(
    name='pywizard',
    version='0.5.12',
    packages=[
        'pywizard',
        'pywizard.resources',
        'pywizard.utils',
    ],

    package_data={
        'pywizard': [
            'templates/*'
        ]
    },

    entry_points={
        'console_scripts': [
            'pywizard = pywizard.cli:pywizard_cmd',
            'pywizard-agent = pywizard.agent:pywizard_agent_cmd',
            'pywizard-context = pywizard.config:pywizard_cfg_cmd',
        ],
    },

    url='',
    license='MIT',
    author='Aleksandr Rudakov',
    author_email='ribozz@gmail.com',
    description='Tool that implements chef/puppet -like approach for server management.',
    long_description=open('README.md').read(),
    install_requires=[
        "jinja2", "iniparse", "argparse", "psutil", "prettytable"
    ],

    tests_require=[
        'pytest',
        'mock'
    ],

    # cmdclass={'test': PyTest},

    extras_require={
        'agent': ['tornado', 'pyzmq'],
        'dev': ['sphinx']
    }
)
