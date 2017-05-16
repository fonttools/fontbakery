# -*- coding: <encoding name> -*-
from __future__ import absolute_import, print_function, unicode_literals

import inspect # will be used

class FontBakeryTest(object):
    def __init__(self, testfunc,
                 id,
                 description, # short text
                 name = None, # very short text
                 conditions=None,
                 arguments_setup=None,
                 documentation=None, # long text, markdown?
                 advancedMessageSetup=None,
                 priority=None
                 ):
        """This is the base class for all tests. It will usually
        not be used directly to create test instances, rather
        decorators which are factories will init this class.

        Arguments:
        testfunc: callable, the test implementation itself.

        id: use reverse domain name notation as a namespace and a
        unique identifier (numbers or anything) but make sure that
        it **never** **ever** changes, that it is **unique until
        eternity**. This is meant to provide a way to track
        burn-down or regressions in a project over time and maybe
        to identify changed/updated test implementations for partial
        spec re-evaluation (in contrast to full spec evaluation) if
        the spec/test changed but not the font.

        description: text, used as one line short description
        read by humans

        name: text, used as a short label read by humans, defaults
        to testfunc.__name__

        conditions: a list of condition names that must be all true
        in order for this test to be executed. conditions are similar
        to tests, because they also inspect the test subject and they
        also belong to the spec. However, they do not get reported
        directly (there could be tests that report the result of a
        condition). Conditions are **probably** registered and
        referenced by name (like "isVariableFont"). We may accept a
        python function for combining or negating a condition. It
        receives the condition values as arguments, queried by name
        via inspection, and returns True or False.
        TODO: flesh out the format.

        arguments_setup: describes the arguments and position/keyword
        of arguments `testfunc` expects. Used to override any arguments
        inferred via inspection of `testfunc`.
        `TestRunner._get_test_dependencies` will use this information
        to prepare the `args` and `kwargs` for this test.
        TODO: flesh out the format.

        documentation: text, used as a detailed documentation,
        read by humans(I suggest to make it markdown formatted).

        advancedMessageSetup: depending on the instance of
        AdvancedMessageType returned by the test, this is the
        counterpart for it. Needed to make sense/use of an
        advancedMessage.
        TODO: Make a proposal for this.
        TODO: This would be used to fix/hotfix issues etc. that means,
              advancedMessageSetup would know how to fix an issue by
              looking at an advancedMessage.
        TODO: The naming is a bit odd.

        priority: inherted from our legacy tests. Need to see if we
        use this at all now.
        """
        self._testfunc = testfunc
        self._id = id
        self._name = testfunc.__name__ if name is None else name
        self._name = name
        self._description = description
        self._arguments_setup = arguments_setup
        self._conditions_setup = conditions_setup
        self._documentation = documentation
        self._advancedMessageSetup = advancedMessageSetup


    # TODO: define public interfaces. The internal state of this
    # object may however not be changed after initialization.
    # Each call to __call__ with the same arguments must return
    # the same result.

    def __call__(self, *args, **kwds):
        # override for special cases?
        return self._testfunc(*args, **kwds)


def fontBakeryTest(*args, **kwds):
    """Test wrapper, a factory for FontBakeryTest

    Requires all arguments of FontBakeryTest but not `testfunc`
    which is passed via the decorator syntax.
    """
    def wrapper(testfunc):
        return FontBakeryTest(testfunc, *args, **kwds)
    return wrapper
