"""
Describe smallest pieces of pywizard domain model
"""

class CanNotResolveConflictError(Exception):
    """
    Exception is thrown when resource conflict (couple of resources with same id)
    can not be resolved.
    """
    pass


class Item(object):
    """
    Base class for Resource and ResourceSet
    """

    _executed = False

    """
    NB! Variable should not be accessed directly, because in feature it will
    be removed. is_executed method will ask from execution state provider
    instead.
    """

    def mark_executed(self):
        """
        Mark current resource executed. Should be called right after
        successful execution of resource.

        This method may be called several times for same Item and this behaviour
        should not cause any side-effects, like multiple remote database triggering.

        Status should be also passed to the backing execution state provider.
        """
        self._executed = True

    def is_executed(self):
        """
        If this method returns True. Resource should not be executed at all.
        """
        return self._executed

    def reset(self):
        """
        Forcibly mark resource as non-executed.

        Status should be also passed to the backing execution state provider.
        """
        self._executed = False

    def apply(self):
        """
        This method is called every time resource should be applied to server.

        Method should check if some changes needed to be done, and execute proper actions if needed.
        """
        pass

    def rollback(self):
        """
        This method is executed when system request to rollback all the changes
        made on server by this resource.

        Method should check if some changes needed to be done, and execute proper actions if needed.
        """
        pass


class Resource(Item):
    """
    Class describe the structure of a Resource
    """

    def describe(self):
        """
        Should return human readable description of resource instance.
        """
        pass

    def get_resource_keys(self):
        """
        Should generate unique for each resource, resource instances that belong to the same
        physical resource (ex. same file or user) should have same id.

        Method should return set() with resource ids.

        @return set
        """
        return set()

    def resolve_conflict(self, resource):
        """
        This method will be called if Resource conflict happens (couple of resources with same id)

        Resource should update own properties with data from conflicting resources or raise
        an exception.

        NB! If type of resource is different (and also not Superclass or subclass) exception
        will be thrown automatically.

        @param resource: Conflicting resource instance

        """
        pass

