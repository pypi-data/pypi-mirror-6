# -*- coding: utf-8 -*-

''' Multimethods

An implementation of multimethods for Python, heavily influenced by
the Clojure programming language.

Copyright (C) 2010-2011 by Daniel Werner.

Improvements by Jeff Weiss and others.

See the README file for information on usage and redistribution.
'''
import types

# only if not already defined, prevents mismatch when reloading modules
if not 'Default' in globals():
    class DefaultMethod(object):
        def __repr__(self):
            return '<DefaultMethod>'

    Default = DefaultMethod()


if not 'Anything' in globals():
    class AnythingType(object):
        def __repr__(self):
            return '<Anything>'

    Anything = AnythingType()


def _parents(x):
    return (hasattr(x, '__bases__') and x.__bases__) or ()


def _is_a(x, y):
    '''Returns true if
    x == y or  x is a subclass of y.
    Works with tuples by calling _is_a on their corresponding elements.
    '''

    def both(a, b, typeslist):
        return isinstance(a, typeslist) and isinstance(b, typeslist)
    if x == y or y is Anything:
        return True
    if both(x, y, (tuple)):
        return all(map(_is_a, x, y))
    else:
        return both(x, y, (type, types.ClassType)) and issubclass(x, y)


def type_dispatch(*args, **kwargs):
    return tuple(type(x) for x in args)


def single_type_dispatch(*args, **kwargs):
    return type(args[0])


class DispatchException(Exception):
    pass


class MultiMethod(object):

    def __init__(self, name, dispatchfn):
        if not callable(dispatchfn):
            raise TypeError('dispatch function must be a callable')

        self.dispatchfn = dispatchfn
        self.methods = {}
        self.preferences = {}
        self.__name__ = name

    def __call__(self, *args, **kwds):
        dv = self.dispatchfn(*args, **kwds)
        best = self.get_method(dv)
        return self.methods[best](*args, **kwds)

    def addmethod(self, func, dispatchval):
        self.methods[dispatchval] = func

    def removemethod(self, dispatchval):
        del self.methods[dispatchval]

    def get_method(self, dv):
        target = self.find_best_method(dv)
        if target:
            return target
        target = self.methods.get(Default, None)
        if target:
            return Default
        raise DispatchException("No matching method on multimethod '%s' for '%s', and "
                                "no default method defined" % (self.__name__, dv))

    def _dominates(self, x, y):
        return self._prefers(x, y) or _is_a(x, y)

    def find_best_method(self, dv):
        best = None
        for k in self.methods:
            if _is_a(dv, k):
                if best is None or self._dominates(k, best):
                    best = k
                    # print best
                # raise if there's multiple matches and they don't point
                # to the exact same method
                if (not self._dominates(best, k)) and \
                   (self.methods[best] is not self.methods[k]):
                    print (best, k, dv)
                    raise DispatchException("Multiple methods in multimethod '%s'"
                                            " match dispatch value %s -> %s and %s, and neither is"
                                            " preferred" % (self.__name__, dv, k, best))
        return best

    def _prefers(self, x, y):
        xprefs = self.preferences.get(x)
        if xprefs is not None and y in xprefs:
            return True
        for p in _parents(y):
            if self._prefers(x, p):
                return True
        for p in _parents(x):
            if self._prefers(p, y):
                return True
        return False

    def prefer(self, dispatchvalX, dispatchvalY):
        if self._prefers(dispatchvalY, dispatchvalX):
            raise Exception("Preference conflict in multimethod '%s':"
                            " %s is already preferred to %s" %
                            (self.__name__, dispatchvalY, dispatchvalX))
        else:
            cur = self.preferences.get(dispatchvalX, set())
            cur.add(dispatchvalY)
            self.preferences[dispatchvalX] = cur

    def methods(self):
        return self.methods

    def method(self, dispatchval):
        def method_decorator(func):
            self.addmethod(func, dispatchval)
            return func
        return method_decorator

    def __repr__(self):
        return "<MultiMethod '%s'>" % self.__name__


def _name(f):
    return "%s.%s" % (f.__module__, f.__name__)


def _copy_attrs(source, dest):
    dest.__doc__ = source.__doc__
    dest.__module__ = source.__module__


def multimethod(dispatch_func):
    '''Create a multimethod that dispatches on the given dispatch_func,
    and uses the given default_func as the default dispatch.  The
    multimethod's descriptive name will also be taken from the
    default_func (its module and name).

    '''
    def multi_decorator(default_func):
        m = MultiMethod(_name(default_func), dispatch_func)
        m.addmethod(default_func, Default)
        _copy_attrs(default_func, m)
        return m
    return multi_decorator


def singledispatch(default_func):
    '''Like python 3.4's singledispatch. Create a multimethod that
    does single dispatch by the type of the first argument. The
    wrapped function will be the default dispatch.
    '''
    m = MultiMethod(_name(default_func), single_type_dispatch)
    m.addmethod(default_func, Default)
    _copy_attrs(default_func, m)
    return m


def multidispatch(default_func):
    '''Create a multimethod that does multiple dispatch by the types of
    all the arguments. The wrapped function will be the default
    dispatch.

    '''
    m = MultiMethod(_name(default_func), type_dispatch)
    m.addmethod(default_func, Default)
    _copy_attrs(default_func, m)
    return m

__all__ = ['MultiMethod', 'type_dispatch', 'single_type_dispatch',
           'multimethod', 'Default', 'multidispatch', 'singledispatch',
           'Anything']
