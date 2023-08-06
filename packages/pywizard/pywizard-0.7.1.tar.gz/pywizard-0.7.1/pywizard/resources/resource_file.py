"""
Resource for manipulating files
"""

import hashlib
from logging import info, debug
from bs4 import BeautifulSoup
import os
from pywizard.resource import Resource, CanNotResolveConflictError, ChangeSetItem
from pywizard.resources.resource_python import PythonResource
from pywizard.templating import compile_content
from pywizard.events import event, event_property
import stat


def file_attribs_get(path):

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

class FileResource(Resource):
    """
    Resource for manipulating files
    """

    remove_mode = False

    on_create = event_property('on_create', """
        Called when file is first created.

        Sample usage::

            nginx = service('nginx')

            my_file = file_('me')
            my_file.on_create = lamda: nginx.reload()

    """)
    on_update = event_property('on_update', 'Called when file is updated')
    on_remove = event_property('on_remove', 'Called when file is removed (on rollback)')

    def __init__(self, path, content=None, is_dir=False):
        self.path = path
        self.content = content
        self.is_dir = is_dir

    def resolve_conflict(self, resource):
        if self.is_dir != resource.is_dir:
            CanNotResolveConflictError('File is marked as directory and file in the same time')

    def get_resource_keys(self):
        return ['file:%s' % self.path]

    def md5sum(self, filename):
        md5 = hashlib.md5()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _content_hash(self):
        content_compiled = compile_content(self.content)
        md5 = hashlib.md5()
        md5.update(content_compiled)
        content_hash = md5.hexdigest()
        return content_hash

    def is_content_update_needed(self):
        """
        Check if content of existing file differs from desired value

        """
        if self.is_dir:
            return False

        content_hash = self._content_hash()
        return content_hash != self.md5sum(self.path)

    def apply(self):

        """
        Creates file or update if it's needed
        """

        content_compiled = compile_content(self.content)

        if os.path.exists(self.path):

            if self.is_content_update_needed():

                def update_content():
                    # s.file_write(self.path, content_compiled, self.mode, self.owner, self.group)
                    with open(self.path, 'w') as f:
                        f.write(content_compiled)

                    event(self.on_update)

                return [ChangeSetItem('Update file content %s' % self.path, update_content)]

            else:
                debug('File with identical content already exist: %s' % self.path)
        else:

            if self.is_dir:
                def create_dir():
                    os.makedirs(self.path)
                    event(self.on_create)
                return [ChangeSetItem('Create dir %s' % self.path, create_dir)]
            else:
                def create_file():
                    with open(self.path, 'w') as f:
                        f.write(content_compiled)
                    event(self.on_create)

                return [ChangeSetItem('Create file %s' % self.path, create_file)]

    def rollback(self):
        """
        Removes file
        """

        if os.path.exists(self.path):
            info('Removing file %s' % self.path)
            if self.is_dir:

                def remove_dir():
                    try:
                        os.rmdir(self.path)
                    except OSError as e:
                        info(e)
                    event(self.on_remove)

                return [ChangeSetItem('Remove dir %s' % self.path, remove_dir)]
            else:
                def remove_file():
                    os.remove(self.path)
                    event(self.on_remove)
                return [ChangeSetItem('Remove file %s' % self.path, remove_file)]
        else:
            debug('File does not exist %s' % self.path)

    def describe(self):
        return 'Create file %s' % self.path

    def to_xml(self):
        el = BeautifulSoup().new_tag('resource')
        if self.is_dir:
            el['class'] = 'directory'
        else:
            el['class'] = 'file'
            el['content-length'] = compile_content(self.content)

        el['path'] = self.path
        return el



def directory(path):
    """
    Creates a directory resource.

    :type path: str
    :param path: Full pathname of new directory
    """
    return FileResource(path, '', True)


def file_(path, content=''):
    """
    Creates a file resource.

    Method has underscore at the end not to override internal python attribute "file" when importing
    pywizard api like this::

        from pywizard.api import *

    Example::

        file_('test.txt')

    File can also accept content::

        file_('test2.txt', content='foo')

    In this case a new file will get content "foo". Also if file exist and content is not same,
    content will be overridden.

    If you need To render something big (as some big config file) consider to use templates.
    See :ref:`templates` for more information.


    :type content: str or callback
    :param content: String or function that return string. Will be used as contents of file.
    :type path: str
    :param path: Full pathname of new file
    """
    return FileResource(path, content, False)


def replace_in_file(path, replacements):
    """
    Takes  and replace each key occurence with it's value.

    :param path: File path
    :type path: basestring

    :param replacements: dictionary of replacements
    :type replacements: dict
    """
    def _apply():
        debug('Replacing data in file %s ' % path)
        debug(replacements)

        with open(path) as f:
            data = f.read()

        for key, value in replacements.items():
            data = data.replace(key, value)

        with open(path, 'w+') as f:
            f.write(data)

    return PythonResource(
        _apply,
        description='Replace in file'
    )


