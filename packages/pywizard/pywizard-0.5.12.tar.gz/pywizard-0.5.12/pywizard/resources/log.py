from logging import INFO
import logging
from pywizard.worker import worker
from pywizard.resource import Resource, CanNotResolveConflictError


class LogResource(Resource):
    def __init__(
            self,
            level=None,
            message=None
    ):
        self.level = level
        self.message = message

    def describe(self):
        return "Log message"

    def apply(self):
        logging.log(self.level, self.message)


def log(message, level=INFO):
    worker.register_resource(
        LogResource(
            level,
            message
        )
    )
