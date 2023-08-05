from logging import debug
import os
from subprocess import CalledProcessError, PIPE, Popen
import psutil
import sys

import logging
import subprocess

logger = logging.getLogger(__name__)


class RequireSudoException(Exception):
    pass


def require_sudo(reason='Unknown'):
    if os.getuid() != 0:
        raise RequireSudoException(reason)

def filter_secrets(text, secrets):
    for secret in secrets:
        text = text.replace(secret, '***SECRET***')
    return text

def run(command, ignore_errors=False, log_output=True, secrets=[]):
    """
    Command is not safe. DO NOT use commands that are composed from untrusted sources
    to execute processes.

    @param command:
    @return:
    """

    debug('Shell command # %s' % filter_secrets(command, secrets))

    out = ''

    try:
        proc = subprocess.Popen(command, shell=isinstance(command, basestring), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline()
            if line != '':
                if log_output:
                    logging.info(line)
                out += line
            else:
                break

        proc.wait()

        proc_returncode = proc.returncode

        if not ignore_errors and proc_returncode != 0:
            raise Exception('Script is failed (return code: %d). Command: %s' % (proc_returncode, filter_secrets(command, secrets)))

    except CalledProcessError as e:
        if not ignore_errors:
            raise e

    return out.strip()


class ProcessList(object):
    def __init__(self, processes):
        """
        @param processes Process[]
        """
        self.processes = processes

    def exist(self):
        return len(self.processes) > 0

    def listens(self, ip, port):
        for p in self.processes:
            for c in p.get_connections():
                if c.status == 'LISTEN':
                    ip_, port_ = c.local_address
                    if ip_ == ip and port == port_:
                        return True
        return False


def find_process(name=None, name_like=None, cmd_like=None, pid=None, username=None):
    """

    :param name:
    :param name_like:
    :param pid:
    :param username:
    :return: pywizrd.utils.process.ProcessList
    """
    if not (name or name_like or cmd_like or pid or username):
        return None

    def match_by_name(p):
        return p.name == name

    def match_by_pid(p):
        return p.pid == pid

    def match_by_username(p):
        return p.username == username

    def match_by_name_like(p):
        return name_like in p.name

    def match_by_cmd_like(p):
        return cmd_like in ' '.join(p.cmdline)

    if name:
        match = match_by_name
    elif pid:
        match = match_by_pid
    elif username:
        match = match_by_username
    elif name_like:
        match = match_by_name_like
    elif cmd_like:
        match = match_by_cmd_like
    else:
        match = match_by_name

    return ProcessList([p for p in psutil.process_iter() if match(p)])