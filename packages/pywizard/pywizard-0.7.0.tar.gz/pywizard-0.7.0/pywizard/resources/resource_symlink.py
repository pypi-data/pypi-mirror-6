from logging import debug
import os
from pywizard.core.env import worker
from pywizard.process import run
from pywizard.resource import Resource


class SymlinkResource(Resource):
    source = None
    destination = None
    use_bind = False

    def __init__(self, source, destination, use_bind=False):
        self.source = source
        self.destination = destination
        self.use_bind = use_bind
        super(SymlinkResource, self).__init__()

    def describe(self):
        return 'Symlink %s -> %s %s' % (self.source, self.destination, '(with mount --bind)' if self.use_bind else '')

    def get_resource_keys(self):
        return 'symlink:%s:%s' % (self.source, self.destination)

    def is_mounted(self, path):
        return path in run('mount -l', ignore_errors=True)

    def rollback(self):
        if self.use_bind:
            if self.is_mounted(self.destination):
                debug('Unmounting ...')
                run('umount %s' % self.destination)
            else:
                debug('Not mounted. Nothing to unmount.')
        else:
            if os.path.exists(self.destination):
                debug('Unlinking ...')
                run('rm %s' % self.destination)
            else:
                debug('Not linked. Nothing to unlink.')

    def apply(self):
        if self.use_bind:
            if not self.is_mounted(self.destination):
                debug('Mounting ...')
                run('mount --bind %s %s' % (self.source, self.destination))
            else:
                debug('Already mounted.')
        else:
            if not os.path.exists(self.destination):
                debug('Linking ...')
                run('ln -s %s %s' % (self.source, self.destination))
            else:
                debug('Already linked.')


def symlink(source, destination, use_bind=False):
    worker.register_resource(
        SymlinkResource(
            source, destination, use_bind
        )
    )
