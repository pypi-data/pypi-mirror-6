"""
Describe smallest pieces of pywizard domain model
"""
from contextlib import contextmanager
from logging import debug
from bs4 import BeautifulSoup


class CanNotResolveConflictError(Exception):
    """
    Exception is thrown when resource conflict (couple of resources with same id)
    can not be resolved.
    """

    def __init__(self, message):
        self.message = message


class ChangeSetItem(object):

    def __init__(self, description, action):
        super(ChangeSetItem, self).__init__()

        self.description = description
        self.action = action

    def commit(self):
        self.action()


class ChangeSet(object):

    def __init__(self, items):
        """
        @type changes: ChangeSetItem[]
        """
        super(ChangeSet, self).__init__()
        self.items = items

    def needed(self):
        return len(self.items) > 0

    def commit(self):
        return [item.commit() for item in self.items]


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

        @return: list of ChangeSetItem
        """
        pass

    def rollback(self):
        """
        This method is executed when system request to rollback all the changes
        made on server by this resource.

        Method should check if some changes needed to be done, and execute proper actions if needed.

        @return: list of ChangeSetItem
        """
        pass

    def to_xml(self):
        """
        Convert cureent item to xml recursively
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

class ResourceSet(Item):
    """
    Declares resource set
    """

    # list of items to execute
    _items = None

    def __init__(self, name):
        self._items = []

        self.name = name
        self.rollback_mode = False

    def describe(self):
        return [r.describe() for r in self._items]

    def add_item(self, item):
        """
        Adds Resource or Resource set item
        @param item: Item
        """
        if not item in self._items:
            self._items.append(item)

    def before_resource_apply(self, resource):
        pass

    def after_resource_apply(self, resource):
        pass

    def before_resource_rollback(self, resource):
        pass

    def after_resource_rollback(self, resource):
        pass

    def rollback(self):
        """
        Rollback resources
        """

        changes = []
        for resource in reversed(self._items):

            debug('=' * 60)
            if not resource.is_executed():

                debug('Rollback: %s' % (resource.describe()))
                self.before_resource_rollback(resource)

                result = resource.rollback()
                if isinstance(result, (list, tuple)):
                    changes += result

                self.after_resource_rollback(resource)
                resource.mark_executed()
            else:
                debug('Skip resource (already rolled back):\t\t %s' % (resource.describe(),))

            debug('=' * 60)

        self.mark_executed()

        return changes

    def apply(self):
        """
        Apply resources,
        """
        if self.rollback_mode:
            return self.rollback()

        debug('#' * 60)
        debug('Resource set: %s' % self.name)
        debug('#' * 60)

        changes = []

        for resource in self._items:

            debug('=' * 60)
            debug('Apply: %s' % (resource.describe(),))
            debug('-' * 60)

            if not resource.is_executed():
                self.before_resource_apply(resource)
                result = resource.apply()
                if isinstance(result, (list, tuple)):
                    changes += result

                self.after_resource_apply(resource)
                resource.mark_executed()
            else:

                debug('Skip resource (already applied):\t\t %s' % (resource.describe(),))
            debug('=' * 60)

        self.mark_executed()

        return changes

    def to_xml(self):
        el = BeautifulSoup().new_tag('resource_set', )
        el['name'] = self.name
        el['rollaback'] = self.rollback_mode
        el['executed'] = self._executed

        if self._items:
            for item in self._items:
                el.append(item.to_xml())
                el.append('\n')

        return el


@contextmanager
def resource_set(ctx, name, rollback=False):
    """
    @type ctx: pywizrd.context.Context
    """
    rs = ResourceSet(name)
    rs.rollback_mode = rollback
    ctx.resource_set_begin(rs)

    yield

    ctx.resource_set_end()


def aggregate_config(instance, key, args, resolve_callback=None, check_callback=None):

    if not hasattr(instance, '_aggregate'):
        instance._aggregate = {}

    if resolve_callback and key in instance._aggregate:
        args = resolve_callback(instance._aggregate[key], args)

    if check_callback:
        check_callback(instance._aggregate, args)

    instance._aggregate[key] = args

    return instance._aggregate
