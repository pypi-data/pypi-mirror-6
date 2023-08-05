from mock import Mock, call
from pywizard.env import Environment

from pywizard.worker import worker


def test_session():
    with worker.session():
        worker.env = 'smth'
        worker.resource_tree = 'smth'
        worker.current_resource_node = 'smth'
        worker.register_with_rollback = 'smth'
        worker.resources = 'smth'
        worker.resource_tree = 'smth'
        worker.resource_set_list = 'smth'
        worker.resource_set_stack = 'smth'
        worker.current_resource_set = 'smth'
        worker.server = 'smth'
        worker.root_resource_set = 'smth'

    assert worker.register_with_rollback is False
    assert isinstance(worker.resources, dict)
    assert len(worker.resources) == 0
    assert isinstance(worker.resource_set_list, list)
    assert len(worker.resource_set_list) == 0
    assert isinstance(worker.resource_set_stack, list)
    assert len(worker.resource_set_stack) == 0
    assert worker.current_resource_set is None
    assert worker.server is None
    assert isinstance(worker.env, Environment)
    assert worker.root_resource_set is None


def test_collect_state():
    with worker.session():
        mock = Mock()

        returned = worker.collect_state(mock)

        print mock.mock_calls == [call()]

        assert returned is None


def test_register_resource_empty():
    with worker.session():
        resource = Mock()
        resource.get_resource_keys.return_value = None

        # should just ignore
        worker.register_resource(resource)


def test_register_resource_two_resources():
    with worker.session():
        resource = Mock()
        resource.get_resource_keys.return_value = [890, 981]

        worker.resources = {123: "hoho", 567: "bebe"} # in real, "hoho" and "bebe" will be resource instances
        worker.current_resource_set = Mock()

        worker.register_resource(resource)

        assert worker.current_resource_set.mock_calls == [call.add_item(resource), call.add_item(resource)]


def test_register_resource_conflicts():
    with worker.session():
        resource = Mock()
        resource2 = Mock()
        resource.get_resource_keys.return_value = [123]

        worker.resources = {123: resource2} # in real, "hoho" and "bebe" will be resource instances
        worker.current_resource_set = Mock()

        worker.register_resource(resource)

        assert resource2.mock_calls == [call.resolve_conflict(resource)]
        assert worker.current_resource_set.mock_calls == [call.add_item(resource2)]


def test_resource_set_begin_end():
    with worker.session():
        assert len(worker.resource_set_stack) == 0
        assert worker.current_resource_set is None
        assert len(worker.resource_set_list) == 0

        resource_set = Mock()
        resource_set.name = 'foo'
        worker.resource_set_begin(resource_set)

        assert len(worker.resource_set_stack) == 1
        assert len(worker.resource_set_list) == 1
        assert worker.current_resource_set == resource_set

        worker.resource_set_end()

        assert len(worker.resource_set_stack) == 0
        assert len(worker.resource_set_list) == 1
        assert worker.current_resource_set is None


def test_resource_set_begin_end_with_rollback():
    with worker.session():
        resource_set = Mock()
        resource_set.name = 'foo'
        worker.register_with_rollback = True
        worker.resource_set_begin(resource_set)

        assert resource_set.rollback_mode is True


