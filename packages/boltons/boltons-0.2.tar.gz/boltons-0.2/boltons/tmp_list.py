from collections import OrderedDict
from operator import itemgetter as _itemgetter


class MutablePoint(list):
    'MutablePoint(x, y)'

    __slots__ = ()

    _fields = ('x', 'y')

    def __new__(cls, x, y):  # TODO: tweak sig to make more extensible
        'Create new instance of MutablePoint(x, y)'
        return list.__new__(cls, (x, y))

    def __init__(self, *a, **kw):
        pass

    @classmethod
    def _make(cls, iterable, new=list.__new__, len=len):
        'Make a new MutablePoint object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 2:
            raise TypeError('Expected 2 arguments,'
                            ' got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        tmpl = self.__class__.__name__ + '(x=%r, y=%r)'
        return tmpl % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new MutablePoint object replacing field(s) with new values'
        result = _self._make(map(kwds.pop, ('x', 'y'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain list.  Used by copy and pickle.'
        return list(self)

    __dict__ = property(_asdict)

    def __getstate__(self):
        'Exclude the OrderedDict from pickling'  # wat
        pass

    x = property(_itemgetter(0), doc='Alias for field 0')

    y = property(_itemgetter(1), doc='Alias for field 1')


if __name__ == '__main__':
    MutablePoint(x=3, y=4)
