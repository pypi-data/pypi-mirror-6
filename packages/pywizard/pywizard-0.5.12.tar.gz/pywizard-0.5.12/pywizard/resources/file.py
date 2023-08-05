"""
Resource for manipulating files
"""

import hashlib
from logging import info, debug
import os
import stat

from pywizard.resources.python import PythonResource
from pywizard.utils.process import run
from pywizard.resource import Resource, CanNotResolveConflictError
from pywizard.templating import compile_content
from pywizard.utils.events import event
from pywizard.worker import worker


class FileResource(Resource):
    """
    Resource for manipulating files
    """

    remove_mode = False

    def __init__(self, path, content=None, mode=None, owner=None, group=None, is_dir=False,
                 on_create=None, on_update=None, on_remove=None, if_exist=None):
        self.path = path
        self.content = content
        self.mode = mode
        self.owner = owner
        self.group = group
        self.is_dir = is_dir
        self.on_create = on_create
        self.on_update = on_update
        self.on_remove = on_remove
        self.if_exist = if_exist

    def resolve_conflict(self, resource):

        if self.is_dir != resource.is_dir:
            CanNotResolveConflictError('File is marked as directory and file in the same time')

        if self.mode is None:
            self.mode = resource.mode
        else:
            if self.mode != resource.mode:
                CanNotResolveConflictError('File uses different mode.')

        if self.owner is None:
            self.owner = resource.owner
        else:
            if self.owner != resource.owner:
                CanNotResolveConflictError('File uses different owner.')

        if self.group is None:
            self.group = resource.group
        else:
            if self.group != resource.group:
                CanNotResolveConflictError('File uses different group.')

                # resolved now

    def get_resource_keys(self):
        return ['file:%s' % self.path]

    def md5sum(self, filename):
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def is_content_update_needed(self):
        """
        Check if content of existing file differs from desired value

        """
        if self.is_dir:
            return False

        content_compiled = compile_content(self.content)
        md5 = hashlib.md5()
        md5.update(content_compiled)
        return md5.hexdigest() != self.md5sum(self.path)

    def is_attribute_update_needed(self):
        """
        Check whether file attributes are different from desired value
        @return:
        """
        return False
        # attributes = self.file_attribs_get(self.path)
        # return attributes['mode'] != self.mode or attributes['owner'] != self.owner or attributes['group'] != self.group

    def apply(self):

        """
        Creates file or update if it's needed
        """

        content_compiled = compile_content(self.content)

        if os.path.exists(self.path):

            if self.is_content_update_needed():

                info('Updating file content %s' % self.path)

                # s.file_write(self.path, content_compiled, self.mode, self.owner, self.group)
                with open(self.path, 'w') as f:
                    f.write(content_compiled)

                event(self.on_update)

            elif self.is_attribute_update_needed():
                pass
                debug('Updating file attributes: %s' % self.path)
                # s.file_attribs(self.path, self.mode, self.owner, self.group)

            else:
                debug('File with identical content already exist: %s' % self.path)
                event(self.if_exist)
        else:
            info('Creating file %s' % self.path)

            if self.is_dir:
                os.makedirs(self.path)
            else:
                with open(self.path, 'w') as f:
                    f.write(content_compiled)

            event(self.on_create)

    def rollback(self):
        """
        Removes file
        """

        if os.path.exists(self.path):
            info('Removing file %s' % self.path)
            if self.is_dir:
                os.rmdir(self.path)
            else:
                os.remove(self.path)

            event(self.on_remove)
        else:
            debug('File does not exist %s' % self.path)

    def describe(self):
        return 'Create file %s' % self.path

    def file_attribs_get(self, path):

        stat_info = os.lstat(path)
        uid = stat_info.st_uid
        gid = stat_info.st_gid

        import pwd
        import grp

        user = pwd.getpwuid(uid)[0]
        group = grp.getgrgid(gid)[0]

        return {
            'mode': oct(stat.S_IMODE(stat_info.st_mode)),
            'user': user,
            'group': group,
            'uid': uid,
            'gid': gid,
        }


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


def directory(path, content='', mode=None, owner=None, group=None,  on_create=None, on_update=None, on_remove=None,
              if_exist=None):
    """
    Generates resource that will create file

    @param path:
    @param content:
    @param mode:
    @param owner:
    @param group:
    """
    worker.register_resource(
        FileResource(
            path, content, mode, owner, group, True, on_create, on_update, on_remove, if_exist
        )
    )


def file_(path, content='', mode=None, owner=None, group=None, on_create=None, on_update=None, on_remove=None,
          if_exist=None
):
    """
    Generates resource that will create file

    @param path:
    @param content:
    @param mode:
    @param owner:
    @param group:
    """
    resource = FileResource(path, content, mode, owner, group, False, on_create, on_update, on_remove, if_exist)
    worker.register_resource(
        resource
    )
    return resource


def replace_in_file(path, replacements):

    def _apply():
        debug('Replacing data in file %s ' % path)
        debug(replacements)

        with open(path) as f:
            data = f.read()

        for key, value in replacements.iteritems():
            data = data.replace(key, value)

        with open(path, 'w+') as f:
            f.write(data)

    worker.register_resource(
        PythonResource(
            _apply,
            description='Replace in file'
        )
    )


