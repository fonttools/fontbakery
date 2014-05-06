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

    def test_upstream(self):
        p = op.join(app.config['ROOT'], 'tests', 'fixtures', 'Font-Italic.ufo')
        r = run_set(p, 'upstream')

        success_tests = r['success']
        tests = map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'failure'), r['failure'])
        tests += map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'error'), r['error'])

        self.assertTrue(is_in_testscases('test_is_A', success_tests))
        # self.assertTrue(is_in_testscases('test_fontname_is_equal_to_macstyle',
        #                                  success_tests), lookup('test_fontname_is_equal_to_macstyle', tests))

    def test_consistency_glyphs(self):
        p = op.join(app.config['ROOT'], 'tests', 'fixtures')
        r = run_set(p, 'consistency')
        failure_tests = r['failure']
        tests = map(lambda x: (str(x), x.id().split('.')[-1], 'success'), r['success'])
        tests += map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'error'), r['error'])

        self.assertTrue(is_in_testscases('test_glyphs_are_consistent_across_family', failure_tests),
                        lookup('test_glyphs_are_consistent_across_family', tests))

    def test_consistency_copyright_notice(self):
        p = op.join(app.config['ROOT'], 'tests', 'fixtures')
        r = run_set(p, 'consistency')

        success_tests = r['success']
        tests = map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'failure'), r['failure'])
        tests += map(lambda x: (str(x._err[1]), x.id().split('.')[-1], 'error'), r['error'])
        self.assertTrue(is_in_testscases('test_copyright_notices_same_across_family', success_tests),
                        lookup('test_copyright_notices_same_across_family', tests))
