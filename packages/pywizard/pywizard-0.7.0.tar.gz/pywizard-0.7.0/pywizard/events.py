from logging import debug
import collections


def event(callback):
    if isinstance(callback, tuple) or isinstance(callback, list):
        return [event(c) for c in callback]
    else:
        if isinstance(callback, collections.Callable):
            return callback()


def event_property(name, doc):

    def getx(self):
        if not hasattr(self, '_event_' + name):
            return []
        return getattr(self, '_event_' + name)

    def setx(self, val):
        if not hasattr(self, '_event_' + name):
            setattr(self, '_event_' + name, [val])
        else:
            old_val = getx(self)
            old_val.append(val)
            setattr(self, '_event_' + name, old_val)

    def delx(self):
        del getx(self)[:]

    return property(getx, setx, delx, doc)
