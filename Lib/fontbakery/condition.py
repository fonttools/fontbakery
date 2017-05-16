# -*- coding: <encoding name> -*-
from __future__ import absolute_import, print_function, unicode_literals


class FontBakeryCondition(object):
    def __init__(self, conditionfunc,
                 name = None, # very short text
                 description = None, # short text
                 arguments_setup=None,
                 documentation=None, # long text, markdown?
                 ):
        self._conditionfunc = conditionfunc
        # use reverse domain name notation when in doubt, to prevent collisions
        # on the other hand, it may be useful to implement a custom function
        # for a commonly used condition.
        self._name = testfunc.__name__ if name is None else name
        self._description = description
        self._arguments_setup = arguments_setup
        self._documentation = documentation


    # TODO: define public interfaces.
    # The return value of __call__ must be the same for the same args,
    # i.e. during a complete TestRunner execution cycle.
    def __call__(self, *args, **kwds):
        # override for special cases?
        return self._conditionfunc(*args, **kwds)


def fontBakeryCondition(*args, **kwds):
    """condition wrapper, a factory for FontBakeryCondition

    Requires all arguments of FontBakeryCondition but not `conditionfunc`
    which is passed via the decorator syntax.
    """
    def wrapper(conditionfunc):
        return FontBakeryCondition(conditionfunc, *args, **kwds)
    return wrapper
