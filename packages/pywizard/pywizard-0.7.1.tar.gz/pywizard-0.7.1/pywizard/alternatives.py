

class Alternative(object):
    """
    Wrapper around callback that supposed to return boolean value.
    *Alternative* allows to implement boolean logic with late execution.
    When boolean logic operators are called new instances of Alternative class are returned,
    allowing to use set of callbacks as object keys::

        package(one_of({
            os_centos() or os_windows(): 'php',
            os_ubuntu(): 'php5'
        }))

    """

    def __init__(self, func):
        self.func = func

    def __or__(self, other):
        return Alternative(lambda: self.func() or other.func())

    def __and__(self, other):
        return Alternative(lambda: self.func() and other.func())

    def __xor__(self, other):
        return Alternative(lambda: self.func() ^ other.func())

    def __nonzero__(self):
        """
        For python 2.x
        """
        return bool(self.func())

    def __bool__(self):
        """
        For python 3.x
        """
        return bool(self.func())


def alternative(func):
    """
    Decorator for boolean function that supposed to be usable for alternatives calculation.
    """
    def callback(*args, **kwargs):

        def exec_callback():
            return func(*args, **kwargs)
        return Alternative(exec_callback)

    callback.__doc__ = func.__doc__

    return callback


def one_of(alternatives):
    """
    Evalutes alternatives using evalute_alternatives() method
    and selects first matched value from result.
    """
    alternatives = evalute_alternatives(alternatives)
    a = alternatives[0] if alternatives else []
    return a


def all_of(alternatives):
    """
    Evalutes alternatives using evalute_alternatives() method
    and collect all values.

    .. note::
        NB! Method expects that every value is list. If it's not, then
        It is converted to list with single item.

    All values from all matched values are merged into one list. If you do need
    list as value, then wrap value with list::

        assert all_of({
            os_ubuntu(): [['foo', 'bar']],
            os_linux(): [['foo', 'bar']],
        }) == [['foo', 'bar'], ['foo', 'bar']]

    While this will merge results::

        assert all_of({
            os_ubuntu(): ['foo', 'bar'],
            os_linux(): ['foo', 'bar'],
        }) == ['foo', 'bar', 'foo', 'bar']

    """
    alternatives = evalute_alternatives(alternatives)
    all_a = []
    for a in alternatives:
        if not isinstance(a, list):
            a = [a]
        all_a.extend(a)
    return set(all_a)


def evalute_alternatives(alternatives):

    if not isinstance(alternatives, dict):
        return alternatives

    found = []
    for key, value in alternatives.items():
        if bool(key) is True:
            found.append(value)

    return found