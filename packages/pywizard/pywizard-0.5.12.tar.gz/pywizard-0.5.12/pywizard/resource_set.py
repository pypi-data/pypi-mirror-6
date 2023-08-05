"""
Resource set main functionality
"""
from logging import debug

from pywizard.resource import Item


class ResourceSet(Item):
    """
    Declares resource set
    """
    name = None

    # list of items to execute
    _items = None

    rollback_mode = False

    def __init__(self, name):
        self._items = []

        self.name = name

    def describe(self):
        return [r.describe() for r in self._items]

    def add_item(self, item):
        """
        Adds Resource or Resource set item
        @param item: Item
        """
        if not item in self._items:
            self._items.append(item)

    def rollback(self):
        """
        Rollback resources
        """

        for resource in self._items:

            debug('=' * 60)
            if not resource.is_executed():

                debug('Rollback: %s' % (resource.describe()))

                resource.rollback()
                resource.mark_executed()
            else:
                debug('Skip resource (already rolled back):\t\t %s' % (resource.describe(),))

            debug('=' * 60)

        self.mark_executed()

    def apply(self):
        """
        Apply resources,
        """
        if self.rollback_mode:
            return self.rollback()

        debug('#' * 60)
        debug('Resource set: %s' % self.name)
        debug('#' * 60)

        for resource in self._items:

            debug('=' * 60)
            debug('Apply: %s' % (resource.describe(),))
            debug('-' * 60)

            if not resource.is_executed():
                resource.apply()
                resource.mark_executed()
            else:

                debug('Skip resource (already applied):\t\t %s' % (resource.describe(),))
            debug('=' * 60)

        self.mark_executed()


