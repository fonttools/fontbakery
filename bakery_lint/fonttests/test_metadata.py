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


class CheckItalicStyleMatchesMacStyle(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def test_check_italic_style_matches_names(self):
        """ METADATA.pb font.style `italic` matches font internals? """
        family = get_FamilyProto_Message(self.operator.path)

        for font_metadata in family.fonts:
            if font_metadata.style != 'italic':
                continue

            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            if not bool(font.macStyle & 0b10):
                self.fail(('Metadata style has been set to italic'
                           ' but font second bit in macStyle has'
                           ' not been set'))

            style = font.familyname.split('-')[-1]
            if not style.endswith('Italic'):
                self.fail(('macStyle second bit is set but postScriptName "%s"'
                           ' is not ended with "Italic"') % font.familyname)

            style = font.fullname.split('-')[-1]
            if not style.endswith('Italic'):
                self.fail(('macStyle second bit is set but fullName "%s"'
                           ' is not ended with "Italic"') % font.fullname)


class CheckNormalStyleMatchesMacStyle(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def test_check_normal_style_matches_names(self):
        """ Check METADATA.pb font.style `italic` matches font internal """
        family = get_FamilyProto_Message(self.operator.path)

        for font_metadata in family.fonts:
            if font_metadata.style != 'normal':
                continue

            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            if bool(font.macStyle & 0b10):
                self.fail(('Metadata style has been set to normal'
                           ' but font second bit (italic) in macStyle has'
                           ' been set'))

            style = font.familyname.split('-')[-1]
            if style.endswith('Italic'):
                self.fail(('macStyle second bit is not set but postScriptName "%s"'
                           ' is ended with "Italic"') % font.familyname)

            style = font.fullname.split('-')[-1]
            if style.endswith('Italic'):
                self.fail(('macStyle second bit is not set but fullName "%s"'
                           ' is ended with "Italic"') % font.fullname)


class CheckMetadataMatchesNameTable(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def test_check_metadata_matches_nametable(self):
        """ Metadata key-value match to table name fields """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            report = '%s: Family name was supposed to be "%s" but is "%s"'
            report = report % (font_metadata.name, fm.name,
                               ttfont.familyname)
            self.assertEqual(ttfont.familyname, fm.name, report)
            self.assertEqual(ttfont.fullname, font_metadata.full_name)


class CheckMenuSubsetContainsProperGlyphs(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def test_check_menu_contains_proper_glyphs(self):
        """ Check menu file contains proper glyphs """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            tf = Font.get_ttfont_from_metadata(self.operator.path, font_metadata, is_menu=True)
            self.check_retrieve_glyphs(tf, font_metadata)

    def check_retrieve_glyphs(self, ttfont, font_metadata):
        cmap = ttfont.retrieve_cmap_format_4()

        glyphs = cmap.cmap

        missing_glyphs = set()
        if ord(' ') not in glyphs:
            missing_glyphs.add(' ')

        for g in font_metadata.name:
            if ord(g) not in glyphs:
                missing_glyphs.add(g)

        if missing_glyphs:
            _ = '%s: Menu is missing glyphs: "%s"'
            report = _ % (font_metadata.filename, ''.join(missing_glyphs))
            self.fail(report)


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


class CheckFontNameNotInCamelCase(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def test_fontname_not_in_camel_case(self):
        """ Check if fontname is not camel cased """
        familymetadata = get_FamilyProto_Message(self.operator.path)

        camelcased_fontnames = []
        for font_metadata in familymetadata.fonts:
            if bool(re.match(r'([A-Z][a-z]+){2,}', font_metadata.name)):
                camelcased_fontnames.append(font_metadata.name)

        if camelcased_fontnames:
            self.fail(('%s are camel cased names. To solve this check just '
                       'use spaces in names.'))


class CheckFontsMenuAgreements(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def menufile(self, font_metadata):
        return '%s.menu' % font_metadata.filename[:-4]

    @tags('required')
    def test_menu_file_agreement(self):
        """ Check fonts have corresponding menu files """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            menufile = self.menufile(font_metadata)
            path = op.join(op.dirname(self.operator.path), menufile)

            if not op.exists(path):
                self.fail('%s does not exist' % menufile)

            if magic.from_file(path) != 'TrueType font data':
                self.fail('%s is not actual TTF file' % menufile)


class CheckFamilyNameMatchesFontNames(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def test_check_familyname_matches_fontnames(self):
        """ Check font name is the same as family name """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            _ = '%s: Family name "%s" does not match font name: "%s"'
            _ = _ % (font_metadata.filename, fm.name, font_metadata.name)
            self.assertEqual(font_metadata.name, fm.name, _)


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


class CheckCanonicalWeights(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def test_check_canonical_weights(self):
        """ Weights have canonical value? """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            weight = font_metadata.weight
            first_digit = weight / 100
            is_invalid = (weight % 100) != 0 or (first_digit < 1
                                                 or first_digit > 9)
            _ = ("%s: The weight is %d which is not a "
                 "multiple of 100 between 1 and 9")

            self.assertFalse(is_invalid, _ % (op.basename(self.operator.path),
                                              font_metadata.weight))

            tf = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            _ = ("%s: METADATA.pb overwrites the weight. "
                 " The METADATA.pb weight is %d and the font"
                 " file %s weight is %d")
            _ = _ % (font_metadata.filename, font_metadata.weight,
                     font_metadata.filename, tf.OS2_usWeightClass)

            self.assertEqual(tf.OS2_usWeightClass, font_metadata.weight)


class CheckPostScriptNameMatchesWeight(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def test_postscriptname_contains_correct_weight(self):
        """ Metadata weight matches postScriptName """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:
            pair = []
            for k, weight in weights.items():
                if weight == font_metadata.weight:
                    pair.append((k, weight))

            if not pair:
                self.fail('Font weight does not match for "postScriptName"')

            if not (font_metadata.post_script_name.endswith('-%s' % pair[0][0])
                    or font_metadata.post_script_name.endswith('-%s' % pair[1][0])):

                _ = ('postScriptName with weight %s must be '
                     'ended with "%s" or "%s"')
                self.fail(_ % (pair[0][1], pair[0][0], pair[1][0]))


class CheckFontWeightSameAsInMetadata(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def test_font_weight_same_as_in_metadata(self):
        """ Font weight matches metadata.pb value of key "weight" """
        fm = get_FamilyProto_Message(self.operator.path)

        for font_metadata in fm.fonts:

            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if font.OS2_usWeightClass != font_metadata.weight:
                msg = 'METADATA.pb has weight %s but in TTF it is %s'
                self.fail(msg % (font_metadata.weight, font.OS2_usWeightClass))


class CheckFullNameEqualCanonicalName(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def test_metadata_contains_current_font(self):
        """ METADATA.pb lists fonts named canonicaly? """

        fm = get_FamilyProto_Message(self.operator.path)

        is_canonical = False
        for font_metadata in fm.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            _weights = []
            for value, intvalue in weights.items():
                if intvalue == font.OS2_usWeightClass:
                    _weights.append(value)

            for w in _weights:
                current_font = "%s %s" % (font.familyname, w)
                if font_metadata.full_name != current_font:
                    is_canonical = True

            if not is_canonical:
                v = map(lambda x: font.familyname + ' ' + x, _weights)
                msg = 'Canonical name in font expected: [%s] but %s'
                self.fail(msg % (v, font_metadata.full_name))


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
