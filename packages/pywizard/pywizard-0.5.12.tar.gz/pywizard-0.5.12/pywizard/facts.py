
import os
import sys
import platform


def available_ips():
    """
    Find all ipv4 interfaces available on system
    @return:
    """
    import netifaces as ni

    # read all ips and filter out ones without ip4
    return [eth[2][0]['addr'] for eth in [ni.ifaddresses(x) for x in ni.interfaces()] if 2 in eth]


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


def is_ubuntu():
    info = os_info()
    return info['distro'] == 'Ubuntu'


def is_centos():
    info = os_info()
    return info['distro'] == 'CentOS'