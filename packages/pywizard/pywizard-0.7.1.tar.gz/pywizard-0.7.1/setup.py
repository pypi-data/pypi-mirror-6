import sys

from setuptools import setup, find_packages


deps = ["jinja2", "distribute", "virtualenv", "beautifulsoup4"]


if sys.version_info[:2] == (2, 6):
    deps.append('argparse')


setup(
    name='pywizard',
    version='0.7.1',
    packages=find_packages(exclude=("test.*",)),

    entry_points={
        'console_scripts': [
            'pywizard = pywizard.cli:pywizard_cmd',
        ],
    },

    url='',
    license='MIT',
    author='Aleksandr Rudakov',
    author_email='ribozz@gmail.com',
    description='Tool that implements chef/puppet -like approach for server management.',
    long_description=open('README.md').read(),
    install_requires=deps,

    # cmdclass={'test': PyTest},

    extras_require={
        'dev': ['pytest', 'coverage', 'pytest-cov', 'mock'],
        'travis': ['coveralls'],
        'docs': ['sphinx==1.2b3', 'sphinx-argparse']
    }
)
