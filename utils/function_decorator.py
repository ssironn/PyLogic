class LogicOperator:
    def __init__(self, functor):
        self.functor = functor
        self.name = functor.__name__
        self.__doc__ = functor.__doc__
        self.mapping = {
            '__add__': 'v',
            '__mul__': '^',
            '__invert__': '¬',
            '__rshift__': '→'
        }

    def __call__(self, *args, **kwargs):
        return self.functor(*args, **kwargs)

    def __repr__(self):
        return '%s' % self.mapping[self.name]
