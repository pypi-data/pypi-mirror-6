import argparse
import json
import sys
import logging

from pywizard.facts import is_ubuntu, is_centos
from pywizard.resources.package_pip import pip_command
from pywizard.utils.process import run, require_sudo
from pywizard.decorators import resource_set
from pywizard.worker import worker


def pywizard_install_requirements(filename):
    run(pip_command('install -r %s' % filename))


def execute_roles(roles):
    if not worker.env.roles or len(worker.env.roles) == 0:
        sys.stderr.write("Given provisioning script requires at least one role to be assigned")
        exit(1)

    for role in worker.env.roles:
        if not role in roles:
            sys.stderr.write("Role %s is not known\n" % role)
            exit(1)

        with resource_set('Role %s' % role):
            for callback in roles[role]:
                callback()


def confirm(prompt_str="Confirm", allow_empty=False, default=False):
    fmt = (prompt_str, 'y', 'n') if default else (prompt_str, 'n', 'y')
    if allow_empty:
        prompt = '%s [%s]|%s: ' % fmt
    else:
        prompt = '%s %s|%s: ' % fmt

    while True:
        ans = raw_input(prompt).lower()

        if ans == '' and allow_empty:
            return default
        elif ans == 'y':
            return True
        elif ans == 'n':
            return False
        else:
            print 'Please enter y or n.'


def check_tornado(try_install=True):
    try:
        __import__('tornado')
    except ImportError:
        if try_install and is_ubuntu() \
            and confirm('Tornado framework is required in order to use pywizard agents. Install it?'):
            require_sudo()
            run('pip install tornado')
            check_zmq(False)
        else:
            sys.stderr.write("\ntornado library should be installed to use pywizard agents.\n")
            exit(1)


def check_zmq(try_install=True):
    try:
        __import__('zmq')
    except ImportError:
        if try_install and (is_ubuntu() or is_centos()) \
            and confirm('ZeroMQ is required in order to use pywizard agents. Install it?'):
            require_sudo()
            if is_ubuntu():
                run('apt-get install -y libzmq-dev')
            if is_centos():
                run('yum install -y zeromq-devel')
            run('pip install pyzmq')
            check_zmq(False)
        else:
            sys.stderr.write("\nzeromq library and pyzmq should be installed to use pywizard agents.\n")
            exit(1)


def json_cmd(command, data=None):
    return json.dumps({'cmd': command, 'data': data})


class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        record.message = record.getMessage()
        # if self.usesTime():
        #     record.asctime = self.formatTime(record, self.datefmt)

        s = self._fmt % record.__dict__
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            try:
                s = s + record.exc_text
            except UnicodeError:
                s = s + record.exc_text.decode(sys.getfilesystemencoding(), 'replace')
        return json_cmd('log', s)


def __atach_agent_logging(socket, topic=None):
    from zmq.log.handlers import PUBHandler

    handler = PUBHandler(socket)
    handler.root_topic = topic
    log_format = "%(message)s"
    handler.formatters = {
        logging.DEBUG: JsonLogFormatter(log_format),
        logging.INFO: JsonLogFormatter(log_format),
        logging.WARN: JsonLogFormatter(log_format),
        logging.ERROR: JsonLogFormatter(log_format),
        logging.CRITICAL: JsonLogFormatter(log_format),
    }
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def __init_agent_logging():
    check_zmq()

    import zmq

    ctx = zmq.Context()

    socket = ctx.socket(zmq.PUB)
    socket.connect('tcp://127.0.0.1:7374')
    print 'Attached to Pywizard agent.'

    __atach_agent_logging(socket)


def check_requirements():
    if sys.version_info < (2, 6, 0):
        sys.stderr.write("Python version that running this script is %d.%d. You need at least "
                         "python 2.6 to run pywizard.\n" % sys.version_info[:2])
        exit(1)

