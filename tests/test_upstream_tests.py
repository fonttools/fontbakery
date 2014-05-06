import os.path as op
import unittest

from bakery.app import app
from checker import run_set


def is_in_testscases(testMethod, list):
    return testMethod in map(lambda x: x.id().split('.')[-1], list)


def lookup(testMethod, testList):
    for t in testList:
        if t[1] == testMethod:
            return '[%s] %s' % (t[2], t[0])


class CheckerTest(unittest.TestCase):

    def test_upstream_tests(self):
        p = op.join(app.config['ROOT'], 'tests', 'fixtures', 'Font-Italic.ufo')
        r = run_set(p, 'upstream')

        success_tests = r['success']
        tests = map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'failure'), r['failure'])
        tests += map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'error'), r['error'])

        self.assertTrue(is_in_testscases('test_is_A', success_tests))
        # self.assertTrue(is_in_testscases('test_fontname_is_equal_to_macstyle',
        #                                  success_tests), lookup('test_fontname_is_equal_to_macstyle', tests))
