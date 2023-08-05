import pwd
from pywizard.utils.process import run
from pywizard.worker import worker
from pywizard.resource import Resource


class UserResource(Resource):
    def __init__(
            self,
            name=None
    ):
        self.name = name

    def describe(self):
        return "Create user"

    def apply(self):
        try:
            pwd.getpwnam(self.name)
        except KeyError:
            run('useradd %s' % self.name)

    def rollback(self):
        try:
            pwd.getpwnam(self.name)
            run('userdel %s' % self.name)
        except KeyError:
            pass


def user(name):
    worker.register_resource(
        UserResource(
            name
        )
    )
