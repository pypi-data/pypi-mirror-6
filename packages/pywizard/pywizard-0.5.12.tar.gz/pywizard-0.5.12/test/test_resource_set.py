from _pytest.python import raises
from mock import Mock
from pywizard.resource_set import ResourceSet


def test_create_instance():
    # nb etree.node is not assigned here! Still should work without any errors
    res = ResourceSet('foo')
    assert res.name == 'foo'


def test_add_item():
    res = ResourceSet('foo')

    assert len(res._items) == 0

    mock = Mock()
    res.add_item(mock)

    assert len(res._items) == 1
    assert res._items[0] == mock


def test_apply_exec_sub_stets():
    mock1 = Mock(spec=ResourceSet)
    mock1.is_executed.return_value = False
    mock2 = Mock(spec=ResourceSet)
    mock2.is_executed.return_value = False
    mock3 = Mock(spec=ResourceSet)
    mock3.is_executed.return_value = False

    res = ResourceSet('foo')
    res.add_item(mock1)
    res.add_item(mock2)
    res.add_item(mock3)

    res.apply()
    mock1.apply.assert_called_once_with()
    mock1.mark_executed.assert_called_once_with()
    mock2.apply.assert_called_once_with()
    mock2.mark_executed.assert_called_once_with()
    mock3.apply.assert_called_once_with()
    mock3.mark_executed.assert_called_once_with()


def test_apply_in_rollback_mode():
    mock1 = Mock(spec=ResourceSet)
    mock1.is_executed.return_value = False
    mock2 = Mock(spec=ResourceSet)
    mock2.is_executed.return_value = False
    mock3 = Mock(spec=ResourceSet)
    mock3.is_executed.return_value = False

    res = ResourceSet('foo')
    res.add_item(mock1)
    res.add_item(mock2)
    res.add_item(mock3)
    res.rollback_mode = True

    res.apply()
    mock1.rollback.assert_called_once_with()
    mock1.mark_executed.assert_called_once_with()
    mock2.rollback.assert_called_once_with()
    mock2.mark_executed.assert_called_once_with()
    mock3.rollback.assert_called_once_with()
    mock3.mark_executed.assert_called_once_with()


def test_rollback_exec_sub_stets():
    mock1 = Mock(spec=ResourceSet)
    mock1.is_executed.return_value = False
    mock2 = Mock(spec=ResourceSet, return_value=False)
    mock2.is_executed.return_value = False
    mock3 = Mock(spec=ResourceSet, return_value=False)
    mock3.is_executed.return_value = False

    res = ResourceSet('foo')
    res.add_item(mock1)
    res.add_item(mock2)
    res.add_item(mock3)

    res.rollback()
    mock1.rollback.assert_called_once_with()
    mock2.rollback.assert_called_once_with()
    mock3.rollback.assert_called_once_with()


def test_add_item_ignores_duplicate_resources():
    mock1 = Mock(spec=ResourceSet)

    res = ResourceSet('foo')
    res.add_item(mock1)
    res.add_item(mock1)

    assert len(res._items) == 1


def test_resource_set_should_ignore_duplicate_executions():
    mock1 = ResourceSet('boo')
    mock1.apply = Mock()

    res = ResourceSet('foo')
    res.add_item(mock1)

    res.apply()
    res.apply()
    res.apply()
    mock1.apply.assert_called_once_with()

def test_resource_set_should_ignore_duplicate_executions_on_rollback():
    mock1 = ResourceSet('boo')
    mock1.rollback = Mock()

    res = ResourceSet('foo')
    res.add_item(mock1)

    res.rollback()
    res.rollback()
    res.rollback()
    mock1.rollback.assert_called_once_with()



