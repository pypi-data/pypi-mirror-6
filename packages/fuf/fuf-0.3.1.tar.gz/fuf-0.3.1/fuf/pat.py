import sys # For module support
from inspect import isclass, isroutine

_DoesNotExist_ = object()

class OverloadSet(object):
    def __init__(self):
        self._overloads = []
    def __call__(self, *args, **kwargs):
        def try_condition(c, a):
            if isclass(c):
                print("It's a class")
                return isinstance(a, c)
            elif isroutine(c):
                print("It's a function")
                return c(a)
            else:
                print("It's a value")
                return c == a
        for cond, kcond, func in self._overloads:
            if all((
                    len(cond) <= len(args),
                    all(try_condition(c, arg) for c, arg in zip(cond, args)),
                    all(kcond.get(name, _)(kwargs.get(name, _DoesNotExist_)) for name in kcond)
                )):
                return func(*args, **kwargs)
        raise RuntimeError("No match found for arguments %s %s" % (args, kwargs))

    def reg(self, *cond, **kwcond):
        def wrap(f):
            self._overloads.append((cond, kwcond, f))
            return self
        return wrap

def Overload(*constraints, **kconstraints):
    def wrap(f):
        f = getattr(f, "__lastreg__", f)
        name = f.__name__
        mod = sys.modules[f.__module__]
        if not hasattr(mod, name):
            setattr(mod, name, OverloadSet())
        getattr(mod, name).reg(*constraints, **kconstraints)(f)
        getattr(mod, name).__lastreg__ = f
        return getattr(mod, name)
    return wrap


# Constraints
# These exist for convenience

def constraint(func):
    return lambda *args, **kwargs: (lambda arg: func(arg, *args, **kwargs))

_   = Anything = lambda arg: True
Or  = constraint(lambda arg, lpred, rpred: (lpred(arg) or rpred(arg)))
And = constraint(lambda arg, lpred, rpred: (lpred(arg) and rpred(arg)))
Not = constraint(lambda arg, pred: not pred(arg))
Exists =         lambda arg: arg is not _DoesNotExist_
Between =        lambda low, high: constraint(lambda arg: low <= arg < high)

import operator
for op in ["lt", "le", "gt", "ge", "eq", "ne"]:
    globals()[op] = constraint(getattr(operator, op))
Has = constraint(operator.contains)
Is  = constraint(operator.is_)
