""" Contains TestCases for METADATA.pb """
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

import magic
import os
import os.path as op
import re
import requests
from google.protobuf import text_format
from bakery_cli.fonts_public_pb2 import FontProto, FamilyProto
from bakery_cli.ttfont import Font
from bakery_lint.base import BakeryTestCase as TestCase, tags, autofix
from bakery_lint.base import TestCaseOperator


def get_FamilyProto_Message(path):
    metadata = FamilyProto()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, metadata)
    return metadata


class CheckGlyphConsistencyInFamily(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def setUp(self):
        self.familymetadata = get_FamilyProto_Message(self.operator.path)

    def test_the_same_number_of_glyphs_across_family(self):
        """ The same number of glyphs across family? """
        glyphs_count = 0
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if not glyphs_count:
                glyphs_count = len(ttfont.glyphs)

            if glyphs_count != len(ttfont.glyphs):
                self.fail('Family has a different glyphs\'s count in fonts')

    def test_the_same_names_of_glyphs_across_family(self):
        """ The same names of glyphs across family? """
        glyphs = None
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if not glyphs:
                glyphs = len(ttfont.glyphs)

            if glyphs != len(ttfont.glyphs):
                self.fail('Family has a different glyphs\'s names in fonts')

    def test_the_same_encodings_of_glyphs_across_family(self):
        """ The same unicode encodings of glyphs across family? """
        encoding = None
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            cmap = ttfont.retrieve_cmap_format_4()

            if not encoding:
                encoding = cmap.platEncID

            if encoding != cmap.platEncID:
                self.fail('Family has different encoding across fonts')


weights = {
    'Thin': 100,
    'ThinItalic': 100,
    'ExtraLight': 200,
    'ExtraLightItalic': 200,
    'Light': 300,
    'LightItalic': 300,
    'Regular': 400,
    'Italic': 400,
    'Medium': 500,
    'MediumItalic': 500,
    'SemiBold': 600,
    'SemiBoldItalic': 600,
    'Bold': 700,
    'BoldItalic': 700,
    'ExtraBold': 800,
    'ExtraBoldItalic': 800,
    'Black': 900,
    'BlackItalic': 900,
}


class CheckCanonicalStyles(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    CANONICAL_STYLE_VALUES = ['italic', 'normal']
    ITALIC_MASK = 0b10

    def test_check_canonical_styles(self):
        """ Font styles are named canonically? """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            self.assertIn(font_metadata.style, self.CANONICAL_STYLE_VALUES)
            if self.is_italic(font_metadata):
                if font_metadata.style != 'italic':
                    _ = "%s: The font style is %s but it should be italic"
                    self.fail(_ % (font_metadata.filename, font_metadata.style))
            else:
                if font_metadata.style != 'normal':
                    _ = "%s: The font style is %s but it should be normal"
                    self.fail(_ % (font_metadata.filename, font_metadata.style))

    def is_italic(self, font_metadata):
        ttfont = Font.get_ttfont_from_metadata(self.operator.path,
                                               font_metadata)
        return (ttfont.macStyle & self.ITALIC_MASK
                or ttfont.italicAngle
                or self.find_italic_in_name_table(ttfont))

    def find_italic_in_name_table(self, ttfont):
        for entry in ttfont.names:
            if 'italic' in Font.bin2unistring(entry).lower():
                return True

def get_suite(path, apply_autofix=False):
    import unittest
    suite = unittest.TestSuite()

    testcases = [
        CheckItalicStyleMatchesMacStyle,
        CheckNormalStyleMatchesMacStyle,
        CheckMetadataMatchesNameTable,
        CheckMenuSubsetContainsProperGlyphs,
        CheckGlyphConsistencyInFamily,
        CheckFontNameNotInCamelCase,
        CheckFontsMenuAgreements,
        CheckFamilyNameMatchesFontNames,
        CheckCanonicalWeights,
        CheckPostScriptNameMatchesWeight,
        CheckFontWeightSameAsInMetadata,
        CheckFullNameEqualCanonicalName,
        CheckCanonicalStyles,
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
