"""
Decorators for resource set handling.
"""
from pywizard.env import Environment
from pywizard.utils.debug import print_resource_recursive

from pywizard.worker import worker
from pywizard.resource_set import ResourceSet


class pywizard_apply():
    """
    Wrapper that collects and executes collected resources instantly.
    :return:
    """

    args = None

    def __init__(self, **kwargs):
        self.args = kwargs

    def __enter__(self):
        if len(worker.resource_set_list):
            raise Exception('Pywizard context is already created (maybe pywizard_apply is already called)?')
        worker.resource_set_begin(ResourceSet('main'))

    def __exit__(self, exc_type, exc_val, exc_tb):
        worker.resource_set_end()

        if len(worker.resource_set_list):
            worker.resource_set_list[0].apply()



def rollback(fn=None):
    """
    for use as a decorator
    @param fn: callable
    """
    if not fn is None:
        def wrapped(**kwargs):
            """
            Decorator that runs the function with "rollback" flag
            @return: mixed
            """
            worker.register_with_rollback = True
            ret = fn(**kwargs)
            worker.register_with_rollback = False
            return ret

        return wrapped

    class with_rollback():
        """
        for use inside python "with" statement
        """

        def __enter__(self):
            worker.register_with_rollback = True

        def __exit__(self, exc_type, exc_val, exc_tb):
            worker.register_with_rollback = False

    return with_rollback()


def resource_set(arg1=None):
    """
    Opens new resource set context

    @param arg1:
    @return:
    """

    decorated_function = None

    if callable(arg1):
        decorated_function = arg1
        resource_name = decorated_function.__name__
    else:
        resource_name = arg1

    instance = ResourceSet(resource_name)

    if not resource_name:
        raise Exception('Resource should have a name.')

    if decorated_function:
        def wrapped():
            """
            Decorator that runs the function with "rollback" flag
            @return: mixed
            """
            worker.resource_set_begin(instance)
            decorated_function(res=instance)
            worker.resource_set_end()

        return wrapped

    else:
        class with_resource():
            """
            for use inside python "with" statement
            """
            resource_instance = None

            def __init__(self, resource_instance):
                self.resource_instance = resource_instance

            def __enter__(self):
                worker.resource_set_begin(self.resource_instance)
                return instance

            # call is needed because of @resource_set('resource-name') decorator
            def __call__(self, decorated_function):
                resource_instance = self.resource_instance

                def wrapped_with_name():
                    """
                    Decorator that runs the function with "rollback" flag
                    @return: mixed
                    """
                    worker.resource_set_begin(resource_instance)
                    decorated_function(res=resource_instance)
                    worker.resource_set_end()

                return wrapped_with_name

            def __exit__(self, exc_type, exc_val, exc_tb):
                worker.resource_set_end()

        return with_resource(instance)
