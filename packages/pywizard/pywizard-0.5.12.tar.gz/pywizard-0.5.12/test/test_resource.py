from _pytest.python import raises
from pywizard.resource import CanNotResolveConflictError, Item, Resource


def test_exception():
    try:
        raise CanNotResolveConflictError('test')
    except CanNotResolveConflictError as e:
        assert e.message == 'test'


def test_resource():
    class Resource2(Resource):
        def resolve_conflict(self, resource):
            super(Resource2, self).resolve_conflict(resource)

        def describe(self):
            super(Resource2, self).describe()

        def rollback(self):
            super(Resource2, self).rollback()

        def get_resource_keys(self):
            super(Resource2, self).get_resource_keys()

        def apply(self):
            super(Resource2, self).apply()

    res = Resource2()

    assert res.is_executed() is False
    res.mark_executed()
    assert res.is_executed() is True
    res.reset()
    assert res.is_executed() is False

    res.resolve_conflict(None)
    res.describe()
    res.rollback()
    res.apply()
    res.get_resource_keys()