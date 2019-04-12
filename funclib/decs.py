# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''some useful decorators'''



class autorepr:
    '''This provides automatic __repr__ for
    a class decorated with this item.

    Example:
    from funclib.decs import autorepr
    @autorepr
    class C:
        def __init__(self):
            self.l = [5, 6, 7]

    >>>print(C())
    C(l = [5,6,7])
    '''

    @staticmethod
    def repr(obj):
        items = []
        for prop, value in obj.__dict__.items():
            try:
                item = "%s = %r" % (prop, value)
                assert len(item) < 20
            except:
                item = "%s: <%s>" % (prop, value.__class__.__name__)
            items.append(item)

        return "%s(%s)" % (obj.__class__.__name__, ', '.join(items))

    def __init__(self, cls):
        cls.__repr__ = autorepr.repr
        self.cls = cls

    def __call__(self, *args, **kwargs):
        return self.cls(*args, **kwargs)