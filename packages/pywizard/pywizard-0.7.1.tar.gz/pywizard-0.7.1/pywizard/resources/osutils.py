

import os
import sys
import platform
from pywizard.alternatives import alternative


def os_info():

    platform_name = sys.platform

    if platform_name == 'linux2':
        distro, version, distro_id = platform.linux_distribution()
    else:
        distro, version, distro_id = None, None, None

    return {
        'platform': platform_name,
        'distro': distro,
        'version': version,
        'id': distro_id,
    }


def distro():
    return os_info()['distro'].lower()

@alternative
def in_docker_container():
    """
    Detects whether current system is running inside docker container.
    Function relies on docker-specific "container" variable.
    """

    return os.getenv('container') == 'lxc'

@alternative
def os_ubuntu():
    """
    os_ubuntu()
    Check if os is ubuntu
    """
    return distro() == 'ubuntu'

@alternative
def os_centos():
    """
    os_centos()
    Checks if os is centos.
    """
    return distro() == 'centos'


@alternative
def os_linux():
    """
    os_linux()
    Checks if it is linux-like os.
    """
    info = os_info()
    return 'linux' in info['platform']
