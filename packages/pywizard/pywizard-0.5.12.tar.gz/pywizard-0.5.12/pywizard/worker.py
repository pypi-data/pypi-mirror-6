"""
Main functionality of pywizard resides in Worker class
"""
from pywizard.env import Environment
from pywizard.resource_set import ResourceSet

__author__ = 'Alex'


class Worker(object):
    """
    Worker collects resources and builds resource tree
    """

    register_with_rollback = False
    apply_instantly = False

    resources = None
    # this list holds all references to all resources
    resource_set_list = None

    # this list is used as a stack to determine current position inside resource_set tree
    resource_set_stack = None

    current_resource_set = None
    server = None

    root_resource_set = None

    env = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.env = Environment()
        self.register_with_rollback = False
        self.resources = {}
        self.resource_set_list = []
        self.resource_set_stack = []
        self.current_resource_set = None
        self.server = None
        self.root_resource_set = None

    def session(self):
        class WorkerSession:
            worker = None

            def __init__(self, worker):
                self.worker = worker

            def __enter__(self):
                self.worker.reset()
                return self.worker

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.worker.reset()

        return WorkerSession(self)

    def collect_state(self, role):
        """
        Collect resources for role, build resource tree.

        @param role:
        @return ResourceSet
        """
        self.resources = {}

        if self.env.requirements:
            self.resource_set_begin(ResourceSet('module requirements'))
            for requirement in self.env.requirements:
                requirement()
            self.resource_set_end()

        role()  # will collect resources using self.register_resource() method

        if len(self.resource_set_list):
            return self.resource_set_list[0]
        else:
            return None

    # internal methods
    def register_resource(self, resource):
        """
        Register resource or merge if it has conflicting id

        @param resource: Resource
        """

        if self.apply_instantly:
            resource.apply()
            return

        ids = resource.get_resource_keys()

        if ids is None:
            return

        items_to_add = []
        if not ids:
            items_to_add.append(resource)
        else:
            for id_ in ids:
                if self.resources.has_key(id_):
                    self.resources[id_].resolve_conflict(resource)
                    items_to_add.append(self.resources[id_])
                else:
                    self.resources[id_] = resource
                    items_to_add.append(resource)

        for item in items_to_add:
            self.current_resource_set.add_item(item)

    def resource_set_begin(self, resource_set_instance):
        """

        @param resource_set_instance:
        @return:
        """

        if self.register_with_rollback:
            resource_set_instance.rollback_mode = True

        # resource_set stack - push
        self.resource_set_stack.append(resource_set_instance)

        if not self.current_resource_set is None:
            self.current_resource_set.add_item(resource_set_instance)

        self.current_resource_set = resource_set_instance

        # add to resource list
        self.resource_set_list.append(resource_set_instance)

    def resource_set_end(self):
        """
        Switch back to parent resource_set
        """

        # resource_set stack - pop
        self.resource_set_stack.pop()
        if len(self.resource_set_stack) == 0:
            self.current_resource_set = None
        else:
            self.current_resource_set = self.resource_set_stack[-1]


worker = Worker()


