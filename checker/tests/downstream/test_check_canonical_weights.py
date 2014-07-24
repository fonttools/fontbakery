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
import os.path as op

from checker.base import BakeryTestCase as TestCase
from checker.metadata import Metadata
from cli.ttfont import Font


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

    path = '.'
    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_check_canonical_weights(self):
        """ Check that weights have canonical value """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            weight = font_metadata.weight
            first_digit = weight / 100
            is_invalid = (weight % 100) != 0 or (first_digit < 1
                                                 or first_digit > 9)
            _ = ("%s: The weight is %d which is not a "
                 "multiple of 100 between 1 and 9")

            self.assertFalse(is_invalid, _ % (op.basename(self.path),
                                              font_metadata.weight))

            tf = Font.get_ttfont_from_metadata(self.path, font_metadata)
            _ = ("%s: METADATA.json overwrites the weight. "
                 " The METADATA.json weight is %d and the font"
                 " file %s weight is %d")
            _ = _ % (font_metadata.filename, font_metadata.weight,
                     font_metadata.filename, tf.OS2_usWeightClass)

            self.assertEqual(tf.OS2_usWeightClass, font_metadata.weight)


class CheckPostScriptNameMatchesWeight(TestCase):

    path = '.'
    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_postscriptname_contains_correct_weight(self):
        """ Metadata weight matches postScriptName """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

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

    path = '.'
    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_postscriptname_contains_correct_weight(self):
        """ Metadata weight matches postScriptName """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:

            font = Font.get_ttfont_from_metadata(self.path, font_metadata)
            if font.OS2_usWeightClass != font_metadata.weight:
                msg = 'METADATA.JSON has weight %s but in TTF it is %s'
                self.fail(msg % (font_metadata.weight, font.OS2_usWeightClass))
