'''
constraints.py
Matthew Soucy

Builtin constraints for the pattern-matching library in fuf
'''
from functools import update_wrapper
from .pat import try_pred


def constraint(func):
    """
    Create a complex contraint out of a function
    A variation of partial application
    The first argument is the only non-fixed argument.
    That argument is the one being tested.
    constraint can only be used for predicates that require arguments
    """
    return update_wrapper(
            (lambda *args, **kwargs: (lambda arg: func(arg, *args, **kwargs))),
            func)


def Any(arg):
    '''
    Any argument is accepted
    Test is for existence of argument
    Can be used to simply test existence of positional or keyword arguments
    '''
    return True


def Exists(arg):
    '''
    Tests for the existence of an argument
    Deprecated due to design changes in fuf
    '''
    from warnings import warn
    warn("Exists deprecated, use Any instead", DeprecationWarning)
    return Any(arg)


def Yes(arg):
    '''
    Truthiness check
    Essentially the identity function

    Equivalent to Cast(bool) or operator.truth
    '''
    return arg


def No(arg):
    '''
    Falsiness check
    Essentially the not operator

    Equivalent to Not(Yes) or operator.not_
    '''
    return not arg


@constraint
def Or(arg, *preds):
    '''
    Logical disjunction
    Returns true if any of the given predicates are matched
    '''
    return any(try_pred(pred, arg) for pred in preds)


@constraint
def And(arg, *preds):
    '''
    Logical conjunction
    Returns true if all of the given predicates are matched
    '''
    return all(try_pred(pred, arg) for pred in preds)


@constraint
def Not(arg, pred):
    '''
    Logical negation
    Returns the opposite truth value as the result of the predicate
    '''
    return not try_pred(pred, arg)


@constraint
def Between(arg, low, high):
    '''
    Range comparison
    Returns true if the argument is between the given values
    Between implies low <= arg < high, as in the range() behavior

    Equivalent to And(ge(low), lt(high))
    '''
    return low <= arg < high


@constraint
def In(arg, *values):
    '''
    Membership comparison
    Test to see if the argument is one of the provided values
    '''
    return arg in values

@constraint
def Has(arg, value):
    '''
    Membership comparison
    Test to see if the given value is contained within the argument

    Reversed operands of In
    '''
    return value in arg


@constraint
def Cast(arg, conv):
    '''
    Test the conversion of an argument through a function
    Behaves like a "cast" operator with a boolean check
    '''
    return conv(arg)


@constraint
def Is(arg, value):
    '''
    Exact identity comparison
    Determines if the argument is an alias to the given value
    '''
    return arg is value

################################################################################
# Math comparison operators

for op, func in [("lt", lambda x,y: x<y),
              ("le", lambda x,y: x<=y),
              ("gt", lambda x,y: x>y),
              ("ge", lambda x,y: x>=y),
              ("eq", lambda x,y: x==y),
              ("ne", lambda x,y: x!=y)]:
    # Basic conditional operators
    func.__doc__ = 'Comparison operator using '+op
    func.__name__ = op
    globals()[op] = constraint(func)
