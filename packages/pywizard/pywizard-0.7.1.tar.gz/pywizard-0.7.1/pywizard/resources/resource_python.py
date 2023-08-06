from logging import debug
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
            debug('Only if = False : no apply')
            return
        if self.if_not and self.if_not():
            debug('Only if_not = True : no apply')
            return

        self._apply()

    def rollback(self):

        if not self._rollback:
            debug('No rollback defined')
            return

        if self.only_if and self.only_if():
            debug('Only if = True : no rollback')
            return
        if self.if_not and not self.if_not():
            debug('Only if_not = False : no rollback')
            return

        self._rollback()


def python(
        apply,
        rollback=None,
        if_not=None,
        only_if=None,
        description=None):
    """
    Resource executes python code. It accepts two callbacks apply and rollback.
    Method also accepts condition to be checked before executing apply and rollback.

    For rollback condition result is negotiated.
    """

    return PythonResource(
        apply,
        rollback,
        if_not,
        only_if,
        description
    )
