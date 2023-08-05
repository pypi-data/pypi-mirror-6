

def aggregate_config(instance, key, args, resolve_callback=None, check_callback=None):

    if not hasattr(instance, '_aggregate'):
        instance._aggregate = {}

    if resolve_callback and key in instance._aggregate:
        args = resolve_callback(instance._aggregate[key], args)

    if check_callback:
        check_callback(instance._aggregate, args)

    instance._aggregate[key] = args

    return instance._aggregate
