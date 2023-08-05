class Foo(object):

    _foo = None

    @property
    def foo(self, *args, **kwargs):
        if _foo is None:
            _foo = kwargs
        return _foo

if __name__ == "__main__":
    a = Foo()
    b = Foo.foo(a='1', b='2')
    print b