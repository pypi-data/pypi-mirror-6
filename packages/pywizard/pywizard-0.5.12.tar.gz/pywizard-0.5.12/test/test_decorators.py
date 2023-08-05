from _pytest.python import raises
from mock import Mock
from pywizard.decorators import rollback, resource_set, pywizard_apply
from pywizard.resource_set import ResourceSet
from pywizard.worker import worker


def test_rollback_decorator():
    with worker.session():
        @rollback
        def foo():
            assert worker.register_with_rollback is True

        assert worker.register_with_rollback is False

        foo()

        assert worker.register_with_rollback is False


def test_rollback_context_provider():
    with worker.session():
        assert worker.register_with_rollback is False

        with rollback():
            assert worker.register_with_rollback is True

        assert worker.register_with_rollback is False


def test_resource_set_decorator():
    with worker.session():
        @resource_set
        def foo(res=None):
            assert len(worker.resource_set_stack) == 1
            assert worker.current_resource_set.name == 'foo'

        assert worker.current_resource_set is None

        foo()

        assert len(worker.resource_set_stack) == 0
        assert worker.current_resource_set is None


def test_resource_set_decorator_another_name():
    with worker.session():
        @resource_set('bee')
        def foo(res=None):
            assert len(worker.resource_set_stack) == 1
            assert worker.current_resource_set.name == 'bee'

        assert worker.current_resource_set is None

        foo()

        assert len(worker.resource_set_stack) == 0
        assert worker.current_resource_set is None


def test_resource_set_context_provider_another_name():
    with worker.session():
        assert worker.current_resource_set is None

        with resource_set('bee'):
            assert len(worker.resource_set_stack) == 1
            assert worker.current_resource_set.name == 'bee'

        assert len(worker.resource_set_stack) == 0
        assert worker.current_resource_set is None


def test_resource_set_context_provider_empty_name():
    with worker.session():
        with raises(Exception):
            with resource_set():
                pass


def test_resource_set_decorator_nested():
    with worker.session():
        @resource_set
        def boo(res=None):
            assert len(worker.resource_set_stack) == 2
            assert worker.current_resource_set.name == 'boo'

        @resource_set
        def foo(res=None):
            assert len(worker.resource_set_stack) == 1
            assert worker.current_resource_set.name == 'foo'

            boo()

            assert len(worker.resource_set_stack) == 1
            assert worker.current_resource_set.name == 'foo'

        assert worker.current_resource_set is None

        foo()

        assert len(worker.resource_set_stack) == 0
        assert worker.current_resource_set is None


def test_pywizard_apply():
    with worker.session():
        with pywizard_apply():
            mock1 = ResourceSet('boo')
            mock1.apply = Mock()
            worker.resource_set_begin(mock1)
            worker.resource_set_end()

        mock1.apply.assert_called_once_with()
