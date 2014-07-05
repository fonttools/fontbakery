# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import unittest
import mock
import simplejson
import StringIO


from checker.tests import test_check_canonical_filenames as tf_f
from checker.tests import test_check_canonical_styles as tf_s
from checker.tests import test_check_canonical_weights as tf_w
from checker.tests import test_check_familyname_matches_fontnames as tf_fm_eq
from checker.tests import test_check_menu_subset_contains_proper_glyphs as tf_menu
from checker.tests import test_check_metadata_matches_nametable as tf_fm_eq_nt
from checker.tests import test_check_nbsp_width_matches_sp_width as tf_nbsp_eq_sp
from checker.tests import test_check_subsets_exists as tf_subset
from checker.tests import test_check_unused_glyph_data as tf_unused
from checker.tests import test_check_os2_width_class as tf_widthclass
from checker.tests import test_check_no_problematic_formats as tf_pr_fmt
from checker.tests import test_check_hmtx_hhea_max_advance_width_agreement as tf_htmx
from checker.ttfont import Font as OriginFont


def _get_tests(TestCase):
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestCase)


def _run_font_test(TestCase):
    runner = unittest.TextTestRunner(stream=StringIO.StringIO())
    tests = _get_tests(TestCase)
    return runner.run(tests)


class Test_CheckCanonicalFilenamesTestCase(unittest.TestCase):

    @mock.patch.object(tf_f.CheckCanonicalFilenames, 'read_metadata_contents')
    def test_one(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'FamilyName',
                'filename': 'FamilyName-Regular.ttf'
            }]
        })
        result = _run_font_test(tf_f.CheckCanonicalFilenames)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Bold.ttf'
            }]
        })
        result = _run_font_test(tf_f.CheckCanonicalFilenames)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckCanonicalStyles(unittest.TestCase):

    @mock.patch.object(tf_s.CheckCanonicalStyles, 'read_metadata_contents')
    def test_two(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Regular.ttf'
            }]
        })

        class Font(object):
            macStyle = 0
            italicAngle = 0
            names = []

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = tf_s.ITALIC_MASK
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = 0
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.italicAngle = 10
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        class name:
            string = ''

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            n = name()
            n.string = 'italic'
            mocked_get_ttfont.return_value.names.append(n)
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckCanonicalWeights(unittest.TestCase):

    @mock.patch.object(tf_w.CheckCanonicalWeights, 'read_metadata_contents')
    def test_three(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'weight': 50
            }]
        })

        class Font(object):
            OS2_usWeightClass = 400

        # test if font weight less than 100 is invalid value
        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_w.CheckCanonicalWeights)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        # test if font weight larger than 900 is invalid value
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'weight': 901
            }]
        })

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_w.CheckCanonicalWeights)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        # test if range 100..900 is valid values and checked for fonts
        for n in range(1, 10):
            with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
                mocked_get_ttfont.return_value = Font()
                metadata_contents.return_value = simplejson.dumps({
                    'fonts': [{
                        'weight': n * 100
                    }]
                })
                mocked_get_ttfont.return_value.OS2_usWeightClass = n * 100
                result = _run_font_test(tf_w.CheckCanonicalWeights)

            if result.errors:
                self.fail(result.errors[0][1])
            self.assertFalse(bool(result.failures))


class Test_CheckFamilyNameMatchesFontName(unittest.TestCase):

    @mock.patch.object(tf_fm_eq.CheckFamilyNameMatchesFontNames, 'read_metadata_contents')
    def test_four(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family'
            }]
        })
        result = _run_font_test(tf_fm_eq.CheckFamilyNameMatchesFontNames)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'FontName'
            }]
        })
        result = _run_font_test(tf_fm_eq.CheckFamilyNameMatchesFontNames)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckMenuSubsetContainsProperGlyphs(unittest.TestCase):

    @mock.patch.object(tf_menu.CheckMenuSubsetContainsProperGlyphs, 'read_metadata_contents')
    def test_five(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontName',
                'filename': 'FontName-Regular.ttf'
            }]
        })

        class FontS:

            def retrieve_glyphs_from_cmap_format_4(self):
                return dict(map(lambda x: (ord(x), x), 'Font Name'))

        class FontF:

            def retrieve_glyphs_from_cmap_format_4(self):
                return dict(map(lambda x: (ord(x), x), 'FontName'))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontS()
            result = _run_font_test(tf_menu.CheckMenuSubsetContainsProperGlyphs)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontF()
            result = _run_font_test(tf_menu.CheckMenuSubsetContainsProperGlyphs)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckMetadataMatchesNameTable(unittest.TestCase):

    @mock.patch.object(tf_fm_eq_nt.CheckMetadataMatchesNameTable, 'read_metadata_contents')
    def test_six(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'Font Family',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })

        class Font:
            familyname = 'Font Family'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_fm_eq_nt.CheckMetadataMatchesNameTable)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.familyname = 'Arial Font Family'
            result = _run_font_test(tf_fm_eq_nt.CheckMetadataMatchesNameTable)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckNbspWidthMatchesSpWidth(unittest.TestCase):

    @mock.patch.object(tf_nbsp_eq_sp.CheckNbspWidthMatchesSpWidth, 'read_metadata_contents')
    def test_seven(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Font Name'
            }]
        })

        class Font:

            def advanceWidth(self, glyphId):
                return 1680

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_nbsp_eq_sp.CheckNbspWidthMatchesSpWidth)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))


class Test_CheckSubsetsExist(unittest.TestCase):

    @mock.patch.object(tf_subset.CheckSubsetsExist, 'read_metadata_contents')
    def test_eight(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'filename': 'FontName-Regular.ttf'
            }],
            'subsets': ['cyrillic']
        })

        with mock.patch.object(tf_subset.File, 'exists') as exists, mock.patch.object(tf_subset.File, 'size') as size:
            size.return_value = 11
            result = _run_font_test(tf_subset.CheckSubsetsExist)
            if result.errors:
                self.fail(result.errors[0][1])
            self.assertFalse(bool(result.failures))
            exists.assert_called_with('FontName-Regular.cyrillic')
            self.assertEqual(size.call_args_list,
                             [mock.call('FontName-Regular.cyrillic'),
                              mock.call('FontName-Regular.ttf')])


class Test_CheckUnusedGlyphData(unittest.TestCase):

    def test_nine(self):

        class Font:

            def get_glyf_length(self):
                return 1234

            def get_loca_glyph_offset(self, num):
                return 1200

            def get_loca_glyph_length(self, num):
                return 34

            def get_loca_num_glyphs(self):
                return 123

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_unused.CheckUnusedGlyphData)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))


class Test_CheckOS2WidthClass(unittest.TestCase):

    def test_ten(self):

        class Font:
            OS2_usWidthClass = 4

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_widthclass.CheckOS2WidthClass)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            for i in [0, 10]:
                mocked_get_ttfont.return_value.OS2_usWidthClass = i
                result = _run_font_test(tf_widthclass.CheckOS2WidthClass)

                if result.errors:
                    self.fail(result.errors[0][1])
                self.assertTrue(bool(result.failures))


class Test_CheckNoProblematicFormats(unittest.TestCase):

    def test_eleven(self):

        class FontTool:

            @staticmethod
            def get_tables(p):
                return ['glyf', 'post', 'GPOS']

        with mock.patch('checker.tests.test_check_no_problematic_formats.FontTool', FontTool):
            result = _run_font_test(tf_pr_fmt.CheckNoProblematicFormats)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))


class Test_CheckHmtxHheaMaxAdvanceWidthAgreement(unittest.TestCase):

    def test_twelve(self):

        class Font:

            def get_hmtx_max_advanced_width(self):
                return 250

            @property
            def advance_width_max(self):
                return 240

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            result = _run_font_test(tf_htmx.CheckHmtxHheaMaxAdvanceWidthAgreement)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))


