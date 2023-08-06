"""
Environment is used as central point for configuration
of any kind.
"""

from bs4 import BeautifulSoup
from pywizard.resource import ResourceSet, ChangeSet


class Environment(dict):
    """
    Provides central place for data exchange
    """

    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self.__dict__ = self


class Context(object):
    """
    Worker collects resources and builds resource tree
    """

    resources = None
    # this list holds all references to all resources
    resource_set_list = None

    # this list is used as a stack to determine current position inside resource_set tree
    resource_set_stack = None

    current_resource_set = None
    root_resource_set = None

    env = None

    def __init__(self):
        self.reset()

    def changeset(self):
        return ChangeSet(self.root_resource_set.apply())

    def reset(self):
        self.env = Environment()
        self.resources = {}
        self.resource_set_list = []
        self.resource_set_stack = []
        self.resource_set_stack = []
        self.current_resource_set = None
        self.root_resource_set = None

    # internal methods
    def register_resource(self, resource):
        """
        Register resource or merge if it has conflicting id

        @param resource: Resource
        """

        ids = resource.get_resource_keys()

        if ids is None:
            return

        items_to_add = []
        if not ids:
            items_to_add.append(resource)
        else:
            for id_ in ids:
                if id_ in self.resources:
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

        current = self.get_current()

        # resource_set stack - push
        self.resource_set_stack.append(resource_set_instance)

        current.add_item(resource_set_instance)

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

    def get_root(self):
        if not self.root_resource_set:
            self.root_resource_set = ResourceSet('root')
            self.current_resource_set = self.root_resource_set
            self.resource_set_stack.append(self.root_resource_set)
            self.resource_set_list.append(self.root_resource_set)
        return self.root_resource_set

    def get_current(self):
        return self.current_resource_set or self.get_root()

    def apply(self, *args):
        res = self.get_current()
        for resource in args:
            res.add_item(resource)

    def to_xml(self):
        root = BeautifulSoup().new_tag("context")
        if self.root_resource_set:
            root.append(self.root_resource_set.to_xml())

        return root


def context(_locals=None):
    """
    :rtype: pywizard.context.Context
    """
    try:
        return _locals['ctx']
    except KeyError:
        return Context()