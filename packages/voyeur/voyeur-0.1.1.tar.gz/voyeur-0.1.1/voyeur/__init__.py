# coding=utf-8
"""
Copyright 2013, Gilles Devaux

All rights reserved.

"""


def is_sequence(_object):
    """
    Check the input is a iteratble but not a string
    :param _object: The object to check
    """
    return not hasattr(_object, "strip") and hasattr(_object, "__iter__")


def get_value(obj, key):
    """
    Get a value from different type of objects

    :param obj: The object to get a value from
    :param key: The key
    :return: The value you want from the object
    """
    try:
        return obj[key]
    except (KeyError, TypeError):
        return getattr(obj, key)


from voyeur.types import Type


def view(data, definition, **kwargs):
    """
    Main entry point to create a view of some data

    :param data: The original data
    :param definition: The definition for creating the view
    :param kwargs: User defined arguments that can be passed to the callables
    :return: The view of the data
    """
    if is_sequence(data) and not isinstance(data, dict):
        return [view(d, definition) for d in data]

    result = {}
    for key, value in definition.items():
        if isinstance(value, dict):  # TODO this could be more generic with __getitem__
            result[key] = view(get_value(data, key), value, **kwargs)
        else:
            if isinstance(value, Type):
                result[key] = value(data, key, **kwargs)
            else:
                try:
                    result[key] = value(get_value(data, key), **kwargs)
                except TypeError:
                    # if the callable does not accept the kwargs
                    result[key] = value(get_value(data, key))

    return result
