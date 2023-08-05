from logging import debug, warn, warning, info, error
from subprocess import CalledProcessError
from pywizard.resource import Resource, CanNotResolveConflictError
from pywizard.utils.events import event
from pywizard.utils.process import run, find_process
from pywizard.worker import worker


class ServiceResource(Resource):
    """
    Resource for manipulating directories
    """

    name = None
    controller = None
    action = None

    on_start = None
    on_restart = None
    on_reload = None
    on_stop = None

    def __init__(self, name, start=True, process_name=None, cmd_line_contains=None):

        self.name = name
        self.process_name = process_name or name
        self.cmd_line_contains = cmd_line_contains
        self._start = start

    def get_key(self):
        return None

    def resolve_conflict(self, resource):
        self._start = resource._start or self._start
        # resolved now

    def get_resource_keys(self):
        return ['service:%s:%s' % (self.get_key(), self.name)]

    def reload(self):
        if self.is_service_running():
            self._exec_action('reload')
            event(self.on_reload)
        else:
            info('Service %s is requested to be reloaded, but it is not running. Reloading.' % self.name)
            self._exec_action('start')
            event(self.on_start)

    def restart(self):
        if self.is_service_running():
            self._exec_action('restart')
            event(self.on_restart)
        else:
            info('Service %s is requested to be restarted, but it is not running. Restarting.' % self.name)
            self._exec_action('start')
            event(self.on_start)

    def start(self):
        if not self.is_service_running():
            self._exec_action('start')
            event(self.on_start)

    def stop(self):
        if not self.is_service_running():
            self._exec_action('stop')
            event(self.on_stop)

    def _exec_action(self, action):
        raise NotImplemented

    def apply(self):
        """
        Starts service
        """
        if self._start:
            if not self.is_service_running():
                debug('Starting.')
                self.start()
            else:
                debug('Service is already started')
        else:
            debug('Delayed start. Skipping service start.')

    def rollback(self):
        """
        Stops service
        """
        if self.is_service_running():
            debug('Stopping.')
            self.stop()
        else:
            debug('Service is not running.')

    def is_service_running(self):
        """
        Checks if service running
        """
        if self.cmd_line_contains:
            process = find_process(cmd_like=self.cmd_line_contains)
        else:
            process = find_process(name_like=self.process_name)
        return process.exist()

    def describe(self):
        return 'Start service %s' % self.name


class UpstartServiceResource(ServiceResource):

    def get_key(self):
        return 'upstart'

    def _exec_action(self, action):

        valid_actions = ('start', 'restart', 'reload')
        if action not in valid_actions:
            raise Exception('Unknown service action "%s". Valid actions for upstart are: %s' % (
                self.action,
                ', '.join(valid_actions)
            ))
        action_ = '%s %s' % (action, self.name)
        debug('Exec action: %s' % action_)
        try:
            run(action_, ignore_errors=True)
        except CalledProcessError as e:
            error('Exec failed: %s' % e.message)


class SysVServiceResource(ServiceResource):

    def get_key(self):
        return 'sysv'

    def _exec_action(self, action):

        try:
            run('service %s %s' % (self.name, action))
        except CalledProcessError as e:
            error('Exec failed: %s' % e.message)


def service(name, controller='sysv', start=True, process_name=None, cmd_line_contains=None):
    """
    Resource for stopping and running services

    @param start:
    @param controller:
    @param name:
    """
    if controller == 'upstart':
        resource = UpstartServiceResource(name, start, process_name, cmd_line_contains)
    elif controller != 'sysv' and issubclass(controller, ServiceResource):
        resource = controller(name, start, process_name, cmd_line_contains)
    else:
        resource = SysVServiceResource(name, start, process_name, cmd_line_contains)

    worker.register_resource(
        resource
    )

    return resource
