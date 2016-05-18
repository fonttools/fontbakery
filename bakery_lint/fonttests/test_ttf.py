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
import fontforge
import magic
import os
import os.path
import re
import StringIO
import sys
import unicodedata


from contextlib import contextmanager
from fontTools import ttLib

from bakery_lint.base import BakeryTestCase as TestCase, tags, autofix, \
    TestCaseOperator
from bakery_cli.fixers import OFLLicenseInfoURLFixer, ApacheLicenseInfoURLFixer, \
    OFLLicenseDescriptionFixer, ApacheLicenseDescriptionFixer
from bakery_cli.fixers import CharacterSymbolsFixer
from bakery_cli.fixers import get_unencoded_glyphs
from bakery_cli.ttfont import Font, FontTool, getSuggestedFontNameValues
from bakery_cli.utils import run, UpstreamDirectory
from bakery_cli.nameid_values import *

@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


def getNameRecordValue(nameRecord):
    return nameRecord.string.decode(nameRecord.getEncoding())


class TTFTestCase(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    def test_fontforge_openfile_contains_stderr(self):
        with redirect_stdout(StringIO.StringIO()) as std:
            fontforge.open(self.operator.path)
            if std.getvalue():
                self.fail('FontForge prints STDERR')

    def test_ttx_family_naming_recommendation(self):
        """ Font follows the family naming recommendations? """
        # See http://forum.fontlab.com/index.php?topic=313.0
        font = Font.get_ttfont(self.operator.path)

        length = len(Font.bin2unistring(font['name'].getName(4, 3, 1, 1033)))
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        length = len(Font.bin2unistring(font['name'].getName(6, 3, 1, 1033)))
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        # <Postscript name> may contain only a-zA-Z0-9
        # and one hyphen
        name = Font.bin2unistring(font['name'].getName(6, 3, 1, 1033))
        self.assertRegexpMatches(name, r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(name.count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        # <Family Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(1, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Style Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(2, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Family Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(16, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Style Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(17, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        if 'OS/2' in font:
            # <Weight> value >= 250 and <= 900 in steps of 50
            self.assertTrue(bool(font['OS/2'].usWeightClass % 50 == 0),
                            msg=('OS/2 usWeightClass has to be in steps of 50.'
                                 ' Now: %s') % font['OS/2'].usWeightClass)

            self.assertGreaterEqual(font['OS/2'].usWeightClass, 250)
            self.assertLessEqual(font['OS/2'].usWeightClass, 900)

        if 'CFF' in font:
            self.assertTrue(bool(font['CFF'].Weight % 50 == 0),
                            msg=('CFF Weight has to be in steps of 50.'
                                 ' Now: %s') % font['CFF'].Weight)

            self.assertGreaterEqual(font['CFF'].Weight, 250)
            self.assertLessEqual(font['CFF'].Weight, 900)

    @autofix('bakery_cli.fixers.CharacterSymbolsFixer')
    def test_check_names_are_ascii_only(self):
        """ Is there any non-ascii character in NAME or CFF tables? """
        font = Font.get_ttfont(self.operator.path)

        for name in font.names:
            # Items with NameID > 18 are expressly for localising
            # the ASCII-only IDs into Hindi / Arabic / etc.
            if name.nameID >= 0 and name.nameID <= 18:
                string = Font.bin2unistring(name)
                marks = CharacterSymbolsFixer.unicode_marks(string)
                if marks:
                    self.fail('Contains {}'.format(marks))

    def assertExists(self, d):
        font = Font.get_ttfont(self.operator.path)
        glyphs = font.retrieve_cmap_format_4().cmap
        if not bool(ord(unicodedata.lookup(d)) in glyphs):
            self.fail('%s does not exist in font' % d)

    def test_euro(self):
        """ Font has 'EURO SIGN' character? """
        self.assertExists('EURO SIGN')

    def test_check_hmtx_hhea_max_advance_width_agreement(self):
        """ MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables? """
        font = Font.get_ttfont(self.operator.path)

        hmtx_advance_width_max = font.get_hmtx_max_advanced_width()
        hhea_advance_width_max = font.advance_width_max
        error = ("AdvanceWidthMax mismatch: expected %s (from hmtx);"
                 " got %s (from hhea)") % (hmtx_advance_width_max,
                                           hhea_advance_width_max)
        self.assertEqual(hmtx_advance_width_max,
                         hhea_advance_width_max, error)

    def test_prep_magic_code(self):
        """ Font contains magic code in PREP table? """
        magiccode = '\xb8\x01\xff\x85\xb0\x04\x8d'
        font = Font.get_ttfont(self.operator.path)
        if 'CFF ' in font: self.skip("Not applicable to a CFF font.")
        try:
            bytecode = font.get_program_bytecode()
        except KeyError:
            bytecode = ''
        self.assertEqual(bytecode, magiccode, msg='No')

    @autofix('bakery_cli.fixers.OpentypeFamilyNameFixer')
    def test_check_opentype_familyname(self):
        """ FamilyName matches Windows-only Opentype-specific FamilyName? """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_family_name, font.familyname)

    @autofix('bakery_cli.fixers.OpentypeFullnameFixer')
    def test_check_opentype_fullname(self):
        """ Fullname matches Windows-only Opentype-specific Fullname? """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_full_name, font.fullname)

    @autofix('bakery_cli.fixers.SubfamilyNameFixer')
    def test_suggested_subfamily_name(self):
        """ Family and style names are set canonically? """
        font = Font.get_ttfont(self.operator.path)
        suggestedvalues = getSuggestedFontNameValues(font.ttfont)
        self.assertEqual(font.familyname, suggestedvalues['family'])
        self.assertEqual(font.stylename, suggestedvalues['subfamily'])

    @tags('required')
    def test_check_names_same_across_platforms(self):
        """ Font names are consistent across platforms? """
        font = Font.get_ttfont(self.operator.path)

        for name in font.names:
            for name2 in font.names:
                if name.nameID != name2.nameID:
                    continue

                if self.diff_platform(name, name2) \
                        or self.diff_platform(name2, name):
                    _name = Font.bin2unistring(name)
                    _name2 = Font.bin2unistring(name2)
                    if _name != _name2:
                        msg = ('Names in "name" table are not the same'
                               ' across specific-platforms')
                        self.fail(msg)

    def diff_platform(self, name, name2):
        return (name.platformID == 3 and name.langID == 0x409
                and name2.platformID == 1 and name2.langID == 0)

    def test_check_os2_width_class(self):
        """ OS/2 width class is correctly set? """
        font = Font.get_ttfont(self.operator.path)
        error = "OS/2 widthClass must be [1..9] inclusive, was %s IE9 fail"
        error = error % font.OS2_usWidthClass
        self.assertIn(font.OS2_usWidthClass, range(1, 10), error)

    def test_check_panose_identification(self):
        """ Is Panose value set correctly? """
        # Check if Panose is not set to monospaced if advancewidth of
        # all glyphs is not equal to each others
        font = Font.get_ttfont(self.operator.path)

        if font['OS/2'].panose.bProportion == 9:
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    link = ('http://www.thomasphinney.com/2013/01'
                            '/obscure-panose-issues-for-font-makers/')
                    self.fail(('Your font does not seem monospaced but PANOSE'
                               ' bProportion set to monospace. It may have '
                               ' a bug in windows. Details: %s' % link))
                prev = font.advance_width(g)

    @tags('note')
    @autofix('bakery_cli.fixers.AddSPUAByGlyphIDToCmap')
    def test_font_unencoded_glyphs(self):
        """ Is there any unencoded glyph? """
        ttx = ttLib.TTFont(self.operator.path, 0)
        unencoded_glyphs = get_unencoded_glyphs(ttx)
        #TODO: Shouldn't we explicitely mention here
        #      which ones are the unencoded glyphs ?
        self.assertIs(unencoded_glyphs, [],
                      msg='There are unencoded glyphs')

    def test_check_upm_heigths_less_120(self):
        """ UPM Heights are NOT greater than 120%? """
        ttfont = Font.get_ttfont(self.operator.path)
        value = ttfont.ascents.get_max() + abs(ttfont.descents.get_min())
        value = value * 100 / float(ttfont.get_upm_height())
        if value > 120:
            _ = "UPM:Height is %d%%, consider redesigning to 120%% or less"
            self.fail(_ % value)

    @tags('required')
    def test_license_included_in_font_names(self):
        """ Check font has a correct license url """
        font = Font.get_ttfont(self.operator.path)

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not regex.match(font.license_url):
            self.fail("LicenseUrl is required and must be correct url")


class FontForgeValidateStateTest(TestCase):

    targets = ['result']
    tool = 'FontForge'
    name = __name__

    def setUp(self):
        font = fontforge.open(self.operator.path)
        self.validation_state = font.validate()

    def test_validation_open_contours(self):
        """ Contours are closed """
        self.assertFalse(bool(self.validation_state & 0x2))

    def test_validation_glyph_intersect(self):
        """ Contours do not intersect """
        self.assertFalse(bool(self.validation_state & 0x4))

    def test_wrong_direction_in_glyphs(self):
        """ Contours have correct directions """
        self.assertFalse(bool(self.validation_state & 0x8))

    def test_flipped_reference_in_glyphs(self):
        """ References in the glyph haven't been flipped """
        self.assertFalse(bool(self.validation_state & 0x10))

    def test_missing_extrema_in_glyphs(self):
        """ Glyphs have points at extremas """
        self.assertFalse(bool(self.validation_state & 0x20))

    def test_referenced_glyphs_are_present(self):
        """ Glyph names referred to from glyphs present in the font """
        self.assertFalse(bool(self.validation_state & 0x40))

    def test_points_are_not_too_far_apart(self):
        """ Points (or control points) are not too far apart """
        self.assertFalse(bool(self.validation_state & 0x40000))

    def test_postscript_hasnt_limit_points_in_glyphs(self):
        """ Not more than 1,500 points in any glyph (a PostScript limit) """
        self.assertFalse(bool(self.validation_state & 0x80))

    def test_postscript_hasnt_limit_hints_in_glyphs(self):
        """ PostScript hasnt a limit of 96 hints in glyphs """
        self.assertFalse(bool(self.validation_state & 0x100))

    def test_valid_glyph_names(self):
        """ Font doesn't have invalid glyph names """
        self.assertFalse(bool(self.validation_state & 0x200))

    def test_allowed_numbers_points_in_glyphs(self):
        """ Glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x400))

    def test_allowed_numbers_paths_in_glyphs(self):
        """ Glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x800))

    def test_allowed_numbers_points_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x1000))

    def test_allowed_numbers_paths_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x2000))

    def test_valid_length_instructions(self):
        """ Glyphs instructions have valid lengths """
        self.assertFalse(bool(self.validation_state & 0x4000))

    def test_points_are_integer_aligned(self):
        """ Points in glyphs are integer aligned """
        self.assertFalse(bool(self.validation_state & 0x80000))

    def test_missing_anchors(self):
        """ Glyphs have all required anchors.
            (According to the opentype spec, if a glyph contains an anchor point
            for one anchor class in a subtable, it must contain anchor points
            for all anchor classes in the subtable. Even it, logically,
            they do not apply and are unnecessary.) """
        self.assertFalse(bool(self.validation_state & 0x100000))

    def test_duplicate_glyphs(self):
        """ Glyph names are unique? """
        self.assertFalse(bool(self.validation_state & 0x200000), 'No. But they should.')

    def test_duplicate_unicode_codepoints(self):
        """ Unicode code points are unique? """
        self.assertFalse(bool(self.validation_state & 0x400000), 'No. But they should.')

    def test_overlapped_hints(self):
        """ Do hints overlap? """
        self.assertFalse(bool(self.validation_state & 0x800000), "Yes. Hints should NOT overlap.")


class CheckFontAgreements(TestCase):

    name = __name__
    targets = ['result']
    tool = 'lint'

    def setUp(self):
        self.font = Font.get_ttfont(self.operator.path)

    @tags('note')
    def test_em_is_1000(self):
        """ Is font em size (ideally) equal to 1000? """
        self.assertEqual(self.font.get_upm_height(), 1000, 'No')

def get_suite(path, apply_autofix=False):
    import unittest
    suite = unittest.TestSuite()

    testcases = [
        TTFTestCase,
        FontForgeValidateStateTest,
        CheckFontAgreements,
    ]

    for testcase in testcases:

        testcase.operator = TestCaseOperator(path)
        testcase.apply_fix = apply_autofix

        if getattr(testcase, 'skipUnless', False):
            if testcase.skipUnless():
                continue

        if getattr(testcase, '__generateTests__', None):
            testcase.__generateTests__()
        
        for test in unittest.defaultTestLoader.loadTestsFromTestCase(testcase):
            suite.addTest(test)

    return suite
