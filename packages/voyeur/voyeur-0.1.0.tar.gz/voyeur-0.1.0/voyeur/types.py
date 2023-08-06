# coding=utf-8
from voyeur import get_value


class Type(object):
    """
    So you can use objects as fields. You need to use an instance.

    The main difference with another callable is that the whole object
     will be passed as the first argument and the key as the second

    >>> class MyType(Type):
    >>>     def __call__(self, *args, **kwargs):
    >>>         return 'domything'
    >>>
    >>> definition = {
    >>>     'field': MyType(),
    >>> }

    """

    def __call__(self, *args, **kwargs):
        return get_value(args[0], args[1])


class DeferredType(Type):
    """
    A type that can read value from another data field.

    You can apply a callable to the value

    >>> from voyeur import view
    >>> definition = {
    >>>     'field': DeferredType('anotherfield', int),
    >>> }
    >>>
    >>> data = {'anotherfield': '2'}
    >>> result = view(data, definition)
    >>> assert result == {'field':2}

    """

    def __init__(self, field, _callable=None):
        """
        Create a new DeferredType

        :param field: The field to get the value from
        :param _callable: An optional callable you want to apply on the value
        """
        self.field = field
        self._callable = _callable

    def __call__(self, *args, **kwargs):
        value = super(DeferredType, self).__call__(args[0], self.field, kwargs)
        if self._callable:
            try:
                return self._callable(value, **kwargs)
            except TypeError:
                return self._callable(value)
        return value
