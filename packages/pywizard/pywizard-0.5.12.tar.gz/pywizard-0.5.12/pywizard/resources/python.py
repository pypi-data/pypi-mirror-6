from pywizard.worker import worker
from pywizard.resource import Resource


class PythonResource(Resource):

    def __init__(
            self,
            apply=None,
            rollback=None,
            if_not=None,
            only_if=None,
            description=None,
        ):
        self._apply = apply
        self._rollback = rollback
        self.if_not = if_not
        self.only_if = only_if
        self.description = description

    def describe(self):
        return "Executes python callback" if not self.description else self.description

    def apply(self):
        if self.only_if and not self.only_if():
            return
        if self.if_not and self.if_not():
            return

        self._apply()

    def rollback(self):

        if not self.rollback:
            return

        if self.only_if and self.only_if():
            return
        if self.if_not and not self.if_not():
            return

        self._rollback()


def python(
        code,
        rollback=None,
        if_not=None,
        only_if=None,
):
    worker.register_resource(
        PythonResource(
            code,
            rollback,
            if_not,
            only_if,
        )
    )
