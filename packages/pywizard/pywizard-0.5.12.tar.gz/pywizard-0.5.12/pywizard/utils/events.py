from logging import debug


def event(callback):
    if isinstance(callback, tuple):
        return [event(c) for c in callback]
    else:
        if callable(callback):
            return callback()

