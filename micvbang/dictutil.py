def get_deep(obj, path, separator='.'):
    """ Retrieve the value denoted by path in obj.

    This is done by recursively calling obj.get([path_head], None) until the path is traversed,
    until a value on the path does not have a callable `get` method, or until the next step in
    the path does not exist. In case the full path cannot be traversed, None is returned.
    """
    if not callable(getattr(obj, 'get', None)):
        return None

    head, *tail = path.split(separator)

    if len(tail) == 0:
        return obj.get(head, None)

    return get_deep(obj.get(head, None), separator.join(tail), separator)
