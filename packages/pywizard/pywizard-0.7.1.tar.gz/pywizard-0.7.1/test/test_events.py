from mock import Mock, call
from pywizard.events import event, event_property


def test_event_single_callback():
    clb = Mock()
    event(clb)

    assert clb.mock_calls == [call()]


def test_event_single_callback_non_callable():
    event("hello")


def test_event_several_callbacks_list():
    clb1 = Mock()
    clb2 = Mock()
    event([clb1, clb2])

    assert clb1.mock_calls == [call()]
    assert clb2.mock_calls == [call()]


def test_event_several_callbacks_tuple():
    clb1 = Mock()
    clb2 = Mock()
    event((clb1, clb2))

    assert clb1.mock_calls == [call()]
    assert clb2.mock_calls == [call()]


def test_event_property():
    class Ho(object):
        on_smth = event_property('on_smth', 'test')

    assert Ho.on_smth.__doc__ == 'test'
    ho1 = Ho()
    assert ho1.on_smth == []
    ho1.on_smth = 'foo'
    assert ho1.on_smth == ['foo']
    ho1.on_smth = 'baz'
    assert ho1.on_smth == ['foo', 'baz']

    del ho1.on_smth
    assert ho1.on_smth == []