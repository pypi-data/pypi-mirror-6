# -*- coding: utf-8 -*-

''' Multimethods

An implementation of multimethods for Python, heavily influenced by
the Clojure programming language.

Copyright (C) 2010-2011 by Daniel Werner.

See the README file for information on usage and redistribution.
'''
import types


class DefaultMethod(object):
    def __repr__(self):
        return '<DefaultMethod>'

Default = DefaultMethod()


def _parents(x):
    return (hasattr(x, '__bases__') and x.__bases__) or ()


def _is_a(x, y):
    '''Returns true if
    x == y or  x is a subclass of y.
    Works with tuples by calling _is_a on their corresponding elements.
    '''

    def both(a, b, typeslist):
        return isinstance(a, typeslist) and isinstance(b, typeslist)
    if x == y:
        return True
    if both(x, y, (tuple)):
        return all(map(_is_a, x, y))
    else:
        return both(x, y, (type, types.ClassType)) and issubclass(x, y)


def type_dispatch(*args):
    return tuple(type(x) for x in args)


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
        del self.methods[dispatchval].multimethod
        del self.methods[dispatchval]

    def get_method(self, dv):
        target = self.find_best_method(dv)
        if target:
            return target
        target = self.methods.get(Default, None)
        if target:
            return Default
        raise Exception("No matching method on multimethod '%s' and "
                        "no default method defined" % self.__name__)

    def _dominates(self, x, y):
        return self._prefers(x, y) or _is_a(x, y)

    def find_best_method(self, dv):
        best = None
        for k in self.methods:
            if _is_a(dv, k):
                if best is None or self._dominates(k, best):
                    best = k
                    # print best
                if not self._dominates(best, k):
                    raise Exception("Multiple methods in multimethod '%s'"
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
                            (self.name, dispatchvalY, dispatchvalX))
        else:
            cur = self.preferences.get(dispatchvalX, set())
            cur.add(dispatchvalY)
            self.preferences[dispatchvalX] = cur

    def methods(self):
        return self.methods

    def method(self, dispatchval):
        def method_decorator(func):
            self.addmethod(func, dispatchval)
            # Return the multimethod itself
            return self
        return method_decorator

    def __repr__(self):
        return "<MultiMethod '%s'>" % self.__name__


def multi(func):
    '''Convenience decorator if you want to use the module and name of your dispatch
    function as the descriptive name for the multimethod.
    @multi
    def mymulti(x, y):
        return (type(x), type(y))

    If you want to use an existing dispatch function, you should just explicitly
    create a MultiMethod object with your own descriptive name:
    mymulti = MultiMethod('mymodule.mymulti', existing_dispatch_fn)

    '''
    name = "%s.%s" % (func.__module__, func.__name__)
    return MultiMethod(name, func)


__all__ = ['MultiMethod', 'type_dispatch', 'multi', 'Default']
