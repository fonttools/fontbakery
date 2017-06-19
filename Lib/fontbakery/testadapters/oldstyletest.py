# -*- coding: <encoding name> -*-
from __future__ import absolute_import, print_function, unicode_literals

from collections import namedtuple
from functools import partial, wraps
from ..testrunner import SKIP, PASS, INFO, WARN, FAIL
from ..test import FontBakeryTest


_FbloggerAPI = namedtuple('FblogAPI',
                       ['skip', 'ok', 'info', 'warning', 'error'])

def _initFbloggerAPI():
    results = []
    def report(status, message):
        results.append((status, message))
    fb = _FbloggerAPI(*[partial(report, status)
                        for status in (SKIP, PASS, INFO, WARN, FAIL)])
    return fb, results

def _gen(result):
    # creates a generator, which we understand
    # in TestRunner._exec_test
    for result in results:
        yield result

class OldStyleTest(FontBakeryTest):
    def __init__(oldstyletest, id, description, *args, **kwargs):
        # we'll inspect the arguments directly from oldstyletest
        super(OldStyleTest, OldStyleTest).__init__(oldstyletest, id,
                                            description, *args, **kwargs)

    def __call__(*args, **kwargs):
        fb, results = _initFbloggerAPI()
        try:
            self._testfunc(fb, *args, **kwargs)
        except Exception as e:
            results.append((FAIL, e))

        return _gen(result)

def oldStyleTest(id, description, *args, **kwds):
    def wrapper(testfunc):
        return return wraps(func)(
                OldStyleTest(testfunc, id, description, *args, **kwds))
    return wrapper
