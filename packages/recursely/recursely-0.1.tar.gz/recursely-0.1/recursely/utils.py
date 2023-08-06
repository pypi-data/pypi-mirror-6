"""
Utility module.
"""
import functools

from recursely._compat import IS_PY3, metaclass


__all__ = ['SentinelList']


class SentinelListMetaclass(type):
    """Metaclass for :class:`SentinelList` that redefines
    all relevant list operations to preserve the sentinels.
    """
    OPERATORS = ['__delitem__', '__iadd__', '__imul__', '__setitem__']
    if not IS_PY3:
        OPERATORS.extend(['__delslice__', '__setslice__'])

    METHODS = ['append', 'extend', 'insert', 'pop',
               'remove', 'reverse', 'sort']

    def __new__(cls, name, bases, dict_):
        """Redefines all state-altering operations to preserve sentinels
        and creates the resulting :class:`list` subclass.
        """
        assert bases == (list,)

        for op in cls.OPERATORS + cls.METHODS:
            dict_[op] = cls.with_preserved_sentinel(op)
        return type.__new__(cls, name, bases, dict_)

    @classmethod
    def with_preserved_sentinel(cls, op):
        """For given :class:`list` operation ``op``, returns a function
        encapsulating it within a code that preserves the sentinel elements
        at the end of list.
        """
        def wrapper(self, *args, **kwargs):
            super_ = super(SentinelList, self)

            sentinels = [super_.pop() for _ in range(self._sentinels_count)]
            sentinels.reverse()
            try:
                return getattr(super_, op)(*args, **kwargs)
            finally:
                super_.extend(sentinels)

        # original methods of ``list`` don't have ``__module__`` attribute,
        # so we need to use ``update_wrapper`` instead of typical ``wraps``
        functools.update_wrapper(wrapper, wrapped=getattr(list, op),
                                 assigned=('__name__', '__doc__'))
        return wrapper


@metaclass(SentinelListMetaclass)
class SentinelList(list):
    """Modified version of standard :class:`list` that always has a `sentinel`
    element(s) at the end, regardless of what modifications we perform on it.
    """
    def __init__(self, iterable, **kwargs):
        """Constructor.

        Single sentinel should be provided as keyword argument ``sentinel``.
        Multiple sentinel element should be provided through ``sentinels``.
        These two arguments are mutually exclusive.

        Other than that, the constructor works the same way as in :class:`list`.
        """
        has_sentinel = 'sentinel' in kwargs
        has_sentinels = 'sentinels' in kwargs
        if not (has_sentinel or has_sentinels):
            raise TypeError('sentinel(s) expected')
        if has_sentinel and has_sentinels:
            raise TypeError('ambiguous sentinel(s)')

        if has_sentinel:
            sentinels = [kwargs['sentinel']]
        else:
            sentinels = list(kwargs['sentinels'])

        super(SentinelList, self).__init__(list(iterable) + sentinels)
        self._sentinels_count = len(sentinels)
