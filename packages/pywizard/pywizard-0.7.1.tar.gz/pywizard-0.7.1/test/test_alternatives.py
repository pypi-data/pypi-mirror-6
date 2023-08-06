from mock import Mock, call
import pytest
from pywizard.alternatives import alternative, Alternative, evalute_alternatives, one_of, all_of


def test_alternative_class_truth():
    a = Alternative(lambda: True)
    assert bool(a) is True

    a = Alternative(lambda: False)
    assert bool(a) is False


def test_alternative_decorator():
    mock = Mock()
    mock.return_value = 'baz'

    a_alternative = alternative(mock)

    a1 = a_alternative('foo')

    assert isinstance(a1, Alternative)
    assert a1.func() == 'baz'
    assert mock.mock_calls == [call('foo')]

def test_alternative_decorator_doc():

    def my_func():
        """
        Foo bar
        """
        pass

    decorated = alternative(my_func)

    assert decorated.__doc__.strip() == "Foo bar"


@pytest.mark.parametrize(("a", "b"), [
    (True, True),
    (True, False),
    (False, True),
    (False, False),
])
def test_or(a, b):
    a1 = Alternative(lambda: a)
    b1 = Alternative(lambda: b)

    a_b = a1 | b1
    assert isinstance(a_b, Alternative)
    assert bool(a_b) is (a or b)


@pytest.mark.parametrize(("a", "b"), [
    (True, True),
    (True, False),
    (False, True),
    (False, False),
])
def test_and(a, b):
    a1 = Alternative(lambda: a)
    b1 = Alternative(lambda: b)

    a_b = a1 & b1
    assert isinstance(a_b, Alternative)
    assert bool(a_b) is (a and b)


@pytest.mark.parametrize(("a", "b"), [
    (True, True),
    (True, False),
    (False, True),
    (False, False),
])
def test_xor(a, b):
    a1 = Alternative(lambda: a)
    b1 = Alternative(lambda: b)

    a_b = a1 ^ b1
    assert isinstance(a_b, Alternative)
    assert bool(a_b) is (a ^ b)


@pytest.mark.parametrize(("a", "b", "c"), [
    (True, True, False),
    (True, False, False),
    (False, True, False),
    (False, False, False),
    (True, True, True),
    (True, False, True),
    (False, True, True),
    (False, False, True),
])
def test_and_or(a, b, c):
    a1 = Alternative(lambda: a)
    b1 = Alternative(lambda: b)
    c1 = Alternative(lambda: c)

    a_b = a1 or (b1 and c1)
    assert isinstance(a_b, Alternative)
    assert bool(a_b) is (a or (b and c))

    a_b = a1 or b1 and c1
    assert isinstance(a_b, Alternative)
    assert bool(a_b) is (a or b and c)


def test_evalute_alternatives_list():
    a = ['foo', 'bar']
    assert evalute_alternatives(a) is a


def test_evalute_alternatives_tuple():
    a = ('foo', 'bar')
    assert evalute_alternatives(a) is a


def test_evalute_alternatives_dict():
    a = {
        False: 'foo',
        True: 'bar'
    }
    result = evalute_alternatives(a)
    assert result == ['bar']


def test_one_of():
    assert ['baz'] == one_of([['baz'], 'bar'])  # whatever do not change typ of element
    assert 'baz' == one_of(['baz', 'bar'])
    assert [] == one_of([])


def test_all_of():
    assert set(('baz', 'bar', 'foo')) == all_of([['baz', 'bar'], 'foo'])  # merge lists
    assert set(('baz', 'foo')) == all_of(['baz', 'foo'])
    assert set() == all_of([])

def compare(s, t):
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t

def test_evalute_alternatives():
    a1 = Alternative(lambda: False)
    a2 = Alternative(lambda: True)
    a3 = Alternative(lambda: True)

    a = {  # order is important for test, usualy dict is also ok
        a1: ['foo', 'bar'],
        a2: 'bar',
        a3: ['foo1', 'bar1'],
    }

    result = evalute_alternatives(a)
    assert compare(result, ['bar', ['foo1', 'bar1']])  # order is not important