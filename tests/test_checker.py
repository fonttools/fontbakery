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

    def assertInSuccess(self, testmethod, testresult):
        success_tests = testresult['success']
        tests = exclude_from_resultlist(testresult, 'success')
        self.assertTrue(check(testmethod, success_tests),
                        lookup(testmethod, tests))

    def assertInFailure(self, testmethod, testresult):
        success_tests = testresult['failure']
        tests = exclude_from_resultlist(testresult, 'failure')
        self.assertTrue(check(testmethod, success_tests),
                        lookup(testmethod, tests))

    def test_upstream(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/src/Font-Italic.ufo')
        r = run_set(p, 'upstream')
        self.assertInSuccess('test_is_A', r)

    def test_results_fontname_is_equal_to_macstyle_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_fontname_is_equal_to_macstyle', run_set(p, 'result'))

    # def test_results_fontname_is_equal_to_macstyle_failure(self):
    #     p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic!.ttf')
    #     self.assertInFailure('test_fontname_is_equal_to_macstyle', run_set(p, 'result'))

    def test_results_nbsp_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_nbsp', run_set(p, 'result'))

    def test_results_nbsp_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_nbsp', run_set(p, 'result'))

    def test_result_space_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_space', run_set(p, 'result'))

    def test_result_space_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Light!.ttf')
        self.assertInFailure('test_space', run_set(p, 'result'))

    def test_result_space_and_nbsp_has_same_advanced_width_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_nbsp_and_space_glyphs_width', run_set(p, 'result'))

    def test_result_space_and_nbsp_has_same_advanced_width_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_nbsp_and_space_glyphs_width', run_set(p, 'result'))

    def test_result_METADATA_family_equals_to_binfont_familyname_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_family', run_set(p, 'result'))

    def test_result_METADATA_family_equals_to_binfont_familyname_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_metadata_family', run_set(p, 'result'))

    def test_result_METADATA_postScriptName_canonical_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_postScriptName_canonical', run_set(p, 'result'))

    def test_result_METADATA_style_matches_postScriptName_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_style_matches_postScriptName', run_set(p, 'result'))

    def test_result_METADATA_filename_matches_postScriptName_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_filename_matches_postScriptName', run_set(p, 'result'))

    def test_result_METADATA_fullname_matches_postScriptName_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_fullname_matches_postScriptName', run_set(p, 'result'))

    def test_result_METADATA_postScriptName_matches_font_filename_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_postScriptName_matches_font_filename', run_set(p, 'result'))

    def test_result_METADATA_postScriptName_matches_internal_fontname_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_postScriptName_matches_internal_fontname', run_set(p, 'result'))

    def test_result_METADATA_style_value_matches_font_italicAngle_value_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_style_value_matches_font_italicAngle_value', run_set(p, 'result'))

    def test_result_font_italicangle_is_zero_or_negative_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_font_italicangle_is_zero_or_negative', run_set(p, 'result'))

    def test_result_font_italicangle_is_zero_or_negative_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic!.ttf')
        self.assertInFailure('test_font_italicangle_is_zero_or_negative', run_set(p, 'result'))

    def test_result_menu_file_exists_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_menu_file_exists', run_set(p, 'result'))

    def test_result_menu_file_exists_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic!.ttf')
        self.assertInFailure('test_menu_file_exists', run_set(p, 'result'))

    def test_result_font_is_font_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_font_is_font', run_set(p, 'result'))

    def test_result_METADATA_font_filename_canonical_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_font_filename_canonical', run_set(p, 'result'))

    def test_result_metadata_fullname_is_equal_to_internal_font_fullname_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_metadata_fullname_is_equal_to_internal_font_fullname', run_set(p, 'result'))

    def test_result_metadata_fullname_is_equal_to_internal_font_fullname_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic!.ttf')
        self.assertInFailure('test_metadata_fullname_is_equal_to_internal_font_fullname', run_set(p, 'result'))

    def test_result_menu_have_chars_for_family_key_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_menu_have_chars_for_family_key', run_set(p, 'result'))

    def test_result_menu_have_chars_for_family_key_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInFailure('test_menu_have_chars_for_family_key', run_set(p, 'result'))

    def test_result_font_subsets_exists_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_font_subsets_exists', run_set(p, 'result'))

    def test_result_font_subsets_exists_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_font_subsets_exists', run_set(p, 'result'))

    def test_result_metadata_family_matches_font_filenames_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_family_matches_font_filenames', run_set(p, 'result'))

    def test_result_metadata_family_matches_font_filenames_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_metadata_family_matches_font_filenames', run_set(p, 'result'))

    def test_result_metadata_value_match_font_weight_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_value_match_font_weight', run_set(p, 'result'))

    def test_result_metadata_value_match_font_weight_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInFailure('test_metadata_value_match_font_weight', run_set(p, 'result'))

    def test_result_metadata_family_values_are_all_the_same(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_family_values_are_all_the_same', run_set(p, 'result'))

    def test_consistency_glyphs_failure(self):
        # TODO: create XXX_success test
        p = op.join(app.config['ROOT'], 'tests/fixtures/src')
        self.assertInFailure('test_glyphs_are_consistent_across_family', run_set(p, 'consistency'))

    def test_consistency_copyright_notice_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/src')
        self.assertInSuccess('test_copyright_notices_same_across_family', run_set(p, 'consistency'))

    def test_result_font_italic_style_matches_internal_font_properties_values_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInSuccess('test_font_italic_style_matches_internal_font_properties_values', run_set(p, 'result'))

    def test_result_font_normal_style_matches_internal_font_properties_values_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_font_normal_style_matches_internal_font_properties_values', run_set(p, 'result'))

    def test_result_subset_file_smaller_font_file_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_subset_file_smaller_font_file', run_set(p, 'result'))

    def test_result_subset_file_smaller_font_file_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Light!.ttf')
        self.assertInFailure('test_subset_file_smaller_font_file', run_set(p, 'result'))

    def test_result_metadata_family_matches_fullname_psname_family_part_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_family_matches_fullname_psname_family_part', run_set(p, 'result'))

    def test_result_metadata_weight_in_range_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_weight_in_range', run_set(p, 'result'))

    def test_result_metadata_weight_in_range_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Regular.ttf')
        self.assertInFailure('test_metadata_weight_in_range', run_set(p, 'result'))

    def test_result_font_has_dsig_table_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Regular.ttf')
        self.assertInSuccess('test_font_has_dsig_table', run_set(p, 'result'))

    def test_result_font_has_dsig_table_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_font_has_dsig_table', run_set(p, 'result'))

    def test_result_license_url_is_included_and_correct_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Regular.ttf')
        self.assertInSuccess('test_license_url_is_included_and_correct', run_set(p, 'result'))

    def test_result_license_url_is_included_and_correct_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        self.assertInFailure('test_license_url_is_included_and_correct', run_set(p, 'result'))

    # TODO: Do not comment until test gets ready
    # def test_result_font_weight_matches_italic_style_success(self):
    #     p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
    #     self.assertInSuccess('test_font_weight_matches_italic_style', run_set(p, 'result'))

    # def test_result_font_weight_matches_italic_style_failure(self):
    #     p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
    #     self.assertInFailure('test_font_weight_matches_italic_style', run_set(p, 'result'))

    def test_result_metadata_designer_exists_in_profiles_csv_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Regular.ttf')
        self.assertInSuccess('test_metadata_designer_exists_in_profiles_csv', run_set(p, 'result'))

    def test_result_is_fsType_not_set_failure(self):
        # TODO: create XXX_success test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Light!.ttf')
        self.assertInFailure('test_is_fsType_not_set', run_set(p, 'result'))

    def test_result_metadata_copyrights_are_equal_for_all_fonts_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_copyrights_are_equal_for_all_fonts', run_set(p, 'result'))

    def test_result_metadata_copyright_matches_pattern_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_copyright_matches_pattern', run_set(p, 'result'))

    def test_result_metadata_copyright_contains_rfn_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_copyright_contains_rfn', run_set(p, 'result'))

    def test_result_metadata_fonts_fields_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        self.assertInSuccess('test_metadata_fonts_fields', r)
        self.assertInSuccess('test_metadata_top_keys_types', r)
        self.assertInSuccess('test_metadata_font_keys_types', r)

    def test_result_metadata_fonts_fields_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Regular.ttf')
        r = run_set(p, 'result')
        self.assertInFailure('test_metadata_fonts_fields', r)
        self.assertInFailure('test_metadata_font_keys_types', r)

    def test_result_metadata_no_unknown_top_keys_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        self.assertInSuccess('test_metadata_no_unknown_top_keys', r)
        self.assertInSuccess('test_metadata_fonts_no_unknown_keys', r)

    def test_result_atleast_latin_menu_subsets_exist_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        self.assertInSuccess('test_latin_file_exists', r)
        self.assertInSuccess('test_menu_file_exists', r)
        self.assertInSuccess('test_metadata_atleast_latin_menu_subsets_exist', r)

    def test_result_atleast_latin_menu_subsets_exist_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold!.ttf')
        r = run_set(p, 'result')
        self.assertInFailure('test_latin_file_exists', r)
        self.assertInFailure('test_menu_file_exists', r)
        self.assertInSuccess('test_metadata_atleast_latin_menu_subsets_exist', r)

    def test_result_each_ttf_subset_menu_truetype_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        r = run_set(p, 'result')
        self.assertInSuccess('test_subsets_files_is_font', r)
        self.assertInSuccess('test_file_is_font', r)
        self.assertInSuccess('test_menu_file_is_font', r)

    def test_result_metadata_has_unique_style_weight_pairs_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_metadata_has_unique_style_weight_pairs', run_set(p, 'result'))

    def test_result_macintosh_platform_names_matches_windows_platform_success(self):
        # TODO: create XXX_failure test
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_macintosh_platform_names_matches_windows_platform', run_set(p, 'result'))

    def test_result_prep_magic_code_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_prep_magic_code', run_set(p, 'result'))

    def test_result_prep_magic_code_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInFailure('test_prep_magic_code', run_set(p, 'result'))

    def test_result_table_gasp_type_success(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertInSuccess('test_table_gasp_type', run_set(p, 'result'))

    def test_result_table_gasp_type_failure(self):
        p = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Italic.ttf')
        self.assertInFailure('test_table_gasp_type', run_set(p, 'result'))
