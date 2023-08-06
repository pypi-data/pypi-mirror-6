import os
from pywizard.core.env import worker
from pywizard.resources.shell import shell


def git_repo(path, bare=True):

    def repo_exist():
        return os.path.exists(path)

    shell(
        'git init %s%s' % ('--bare ' if bare else '', path),
        'rm -rf %s' % path,
        if_not=repo_exist,
        description='Create %srepository at %s' % ('bare ' if bare else '', path)
    )


def git_clone(url, path, branch=None):

    def repo_exist():
        return os.path.exists(path)

    branch_name = ('branch %s' % branch) if branch else ''
    shell(
        'git clone %s%s %s' % (branch or '', url, path),
        'rm -rf %s' % path,
        if_not=repo_exist,
        description='Clone repository %sfrom %s into %s' % (branch_name, url, path)
    )