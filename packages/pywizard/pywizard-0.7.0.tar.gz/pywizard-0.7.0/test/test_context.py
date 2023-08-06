from mock import Mock, call
from pywizard.context import Context, Environment

def test_register_resource_empty():
    context = Context()
    resource = Mock()
    resource.get_resource_keys.return_value = None

    # should just ignore
    context.register_resource(resource)


def test_register_resource_two_resources():
    context = Context()
    resource = Mock()
    resource.get_resource_keys.return_value = [890, 981]

    context.resources = {123: "hoho", 567: "bebe"} # in real, "hoho" and "bebe" will be resource instances
    context.current_resource_set = Mock()

    context.register_resource(resource)

    assert context.current_resource_set.mock_calls == [call.add_item(resource), call.add_item(resource)]


def test_register_resource_conflicts():
    context = Context()
    resource = Mock()
    resource2 = Mock()
    resource.get_resource_keys.return_value = [123]

    context.resources = {123: resource2} # in real, "hoho" and "bebe" will be resource instances
    context.current_resource_set = Mock()

    context.register_resource(resource)

    assert resource2.mock_calls == [call.resolve_conflict(resource)]
    assert context.current_resource_set.mock_calls == [call.add_item(resource2)]


def test_resource_set_begin_end():
    context = Context()
    assert len(context.resource_set_stack) == 0
    assert context.current_resource_set is None
    assert len(context.resource_set_list) == 0

    resource_set = Mock()
    resource_set.name = 'foo'
    context.resource_set_begin(resource_set)

    assert len(context.resource_set_stack) == 2
    assert len(context.resource_set_list) == 2
    assert context.current_resource_set == resource_set

    context.resource_set_end()

    assert len(context.resource_set_stack) == 1
    assert len(context.resource_set_list) == 2
    assert context.current_resource_set == context.root_resource_set

