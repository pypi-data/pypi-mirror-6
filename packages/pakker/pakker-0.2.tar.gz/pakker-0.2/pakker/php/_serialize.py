# encoding: utf-8

from io import BytesIO
from functools import partial

from singledispatch import singledispatch


# Py 3 compat
try:
    long
except NameError:
    long = int
    unicode = str


class _Registry(object):
    def __init__(self):
        self.registered_methods = {}

    def register(self, type_):
        def decorator(f):
            self.registered_methods[type_] = f
            return f
        return decorator

    def apply(self, dispatcher, obj):
        for (type_, func) in self.registered_methods.items():
            dispatcher.register(type_, partial(func, obj))


class _Serializer(object):
    _registry = _Registry()
    serializes = _registry.register

    def __init__(self, outfile, encoding):
        self.outfile = outfile
        self.encoding = encoding
        self._registry.apply(self.serialize, self)

    @serializes(type(None))
    def _(self, obj):
        assert obj is None
        self.outfile.write(b"n;")

    @serializes(bool)
    def _(self, obj):
        if obj:
            self.outfile.write(b"b:1;")
        else:
            self.outfile.write(b"b:0;")

    @serializes(int)
    @serializes(long)
    def _(self, obj):
        self.outfile.write(b'i:')
        self.outfile.write(str(obj).encode('ascii'))
        self.outfile.write(b';')

    @serializes(float)
    def _(self, obj):
        self.outfile.write(b'd:')
        self.outfile.write(str(obj).encode('ascii'))
        self.outfile.write(b';')

    @serializes(bytes)
    def _(self, obj):
        self.outfile.write(b's:')
        self.outfile.write(str(len(obj)).encode('ascii'))
        self.outfile.write(b':"')
        self.outfile.write(obj)
        self.outfile.write(b'";')

    @serializes(unicode)
    def _(self, obj):
        self.serialize(obj.encode(self.encoding))

    @serializes(dict)
    def _(self, obj):
        self.outfile.write(b'a:')
        self.outfile.write(str(len(obj)).encode('ascii'))
        self.outfile.write(b':{')
        for (key, value) in obj.items():
            self.serialize(key)
            self.serialize(value)
        self.outfile.write(b'}')

    @staticmethod
    @singledispatch
    def serialize(obj):
        raise ValueError("Can't serialize object {0!r}".format(obj))


def dumps(obj, encoding="utf-8"):
    outfile = BytesIO()
    dump(obj, outfile, encoding=encoding)
    return outfile.getvalue()


def dump(obj, outfile, encoding="utf-8"):
    serializer = _Serializer(outfile, encoding)
    serializer.serialize(obj)
