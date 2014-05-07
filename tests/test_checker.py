import os.path as op
import unittest

from bakery.app import app
from checker import run_set


def check(testMethod, list):
    try:
        return filter(lambda x: x.id().split('.')[-1] == testMethod, list)[0]
    except IndexError:
        return


def lookup(testMethod, testList):
    for t in testList:
        if t[1] == testMethod:
            return '[%s] %s' % (t[2], t[0])


def checktag(result_test, tag):
    return bool(tag in getattr(result_test, result_test._testMethodName).tags)


def exclude_from_resultlist(resultlist, category):
    tests = []
    lerr = lambda x: (str(x._err[1]), x.id().split('.')[-1], 'error')
    lfle = lambda x: (str(x._err[1]), x.id().split('.')[-1], 'failure')
    lscs = lambda x: (str(x), x.id().split('.')[-1], 'success')
    if category == 'success':
        tests += map(lfle, resultlist['failure'])
    elif category == 'failure':
        tests += map(lscs, resultlist['success'])
    return tests + map(lerr, resultlist['error'])


class CheckerTest(unittest.TestCase):

    def test_upstream(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/src/Font-Italic.ufo')
        r = run_set(p, 'upstream')

        success_tests = r['success']

        # tests = exclude_from_resultlist(r, 'success')
        self.assertTrue(check('test_is_A', success_tests))
        # self.assertTrue(check('test_fontname_is_equal_to_macstyle',
        #                                  success_tests), lookup('test_fontname_is_equal_to_macstyle', tests))

    def test_results_nbsp_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')

        self.assertTrue(check('test_nbsp', success_tests),
                        lookup('test_nbsp', tests))

    def test_results_nbsp_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        r = run_set(p, 'result')
        failure_tests = r['failure']
        tests = exclude_from_resultlist(r, 'failure')

        self.assertTrue(check('test_nbsp', failure_tests),
                        lookup('test_nbsp', tests))

    def test_result_space_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')
        self.assertTrue(check('test_space', success_tests),
                        lookup('test_space', tests))

    def test_result_space_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Light!.ttf')
        r = run_set(p, 'result')
        failure_tests = r['failure']
        tests = exclude_from_resultlist(r, 'failure')
        self.assertTrue(check('test_space', failure_tests),
                        lookup('test_space', tests))

    def test_result_space_and_nbsp_has_same_advanced_width_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')

        result_test = check('test_nbsp_and_space_glyphs_width', success_tests)
        self.assertTrue(result_test,
                        lookup('test_nbsp_and_space_glyphs_width', tests))

    def test_result_space_and_nbsp_has_same_advanced_width_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Regular!.ttf')
        r = run_set(p, 'result')
        failure_tests = r['failure']
        tests = exclude_from_resultlist(r, 'failure')
        result_test = check('test_nbsp_and_space_glyphs_width', failure_tests)
        self.assertTrue(result_test,
                        lookup('test_nbsp_and_space_glyphs_width', tests))

    def test_result_METADATA_family_equals_to_binfont_familyname_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')
        result_test = check('test_metadata_family', success_tests)
        self.assertTrue(result_test,
                        lookup('test_metadata_family', tests))

    def test_result_METADATA_family_equals_to_binfont_familyname_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        r = run_set(p, 'result')
        failure_tests = r['failure']
        tests = exclude_from_resultlist(r, 'failure')
        result_test = check('test_metadata_family', failure_tests)
        self.assertTrue(result_test,
                        lookup('test_metadata_family', tests))

    def test_result_METADATA_postScriptName_canonical_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')
        result_test = check('test_metadata_postScriptName_canonical', success_tests)
        self.assertTrue(result_test,
                        lookup('test_metadata_postScriptName_canonical', tests))

    def test_result_METADATA_style_matches_postScriptName_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')
        result_test = check('test_metadata_style_matches_postScriptName', success_tests)
        self.assertTrue(result_test,
                        lookup('test_metadata_style_matches_postScriptName', tests))

    def test_result_METADATA_filename_matches_postScriptName_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')
        result_test = check('test_metadata_filename_matches_postScriptName', success_tests)
        self.assertTrue(result_test,
                        lookup('test_metadata_filename_matches_postScriptName', tests))

    def test_consistency_glyphs(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/src')
        r = run_set(p, 'consistency')
        failure_tests = r['failure']
        tests = exclude_from_resultlist(r, 'failure')
        self.assertTrue(check('test_glyphs_are_consistent_across_family', failure_tests),
                        lookup('test_glyphs_are_consistent_across_family', tests))

    def test_consistency_copyright_notice(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/src')
        r = run_set(p, 'consistency')

        success_tests = r['success']
        tests = exclude_from_resultlist(r, 'success')
        self.assertTrue(check('test_copyright_notices_same_across_family', success_tests),
                        lookup('test_copyright_notices_same_across_family', tests))
