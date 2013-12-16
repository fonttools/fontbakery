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

from checker.base import BakeryTestCase as TestCase
import fontforge
import yaml
import os

class MetadataJSONTest(TestCase):
    targets = ['result']
    tool   = 'FontForge'
    name   = __name__
    path   = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)
        #
        medatata_path = os.path.join(os.path.dirname(self.path), 'METADATA.json')
        self.metadata = yaml.load(open(medatata_path, 'r').read())

    def test_metadata_family(self):
        """ Font and METADATA.json have the same name """
        self.assertEqual(self.font.fontname.split('-').pop(0), self.metadata.get('name', None))

    def test_metadata_font_have_regular(self):
        """ According GWF standarts font should have Regular style. """
        # this tests will appear in each font
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular'):
                have = True

        self.assertTrue(have)

    def test_metadata_regular_is_400(self):
        """ Usually Regular should be 400 """
        # XXX: Dave, check if this test is needed
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular') and int(i['weight']) == 400:
                have = True

        self.assertTrue(have)

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        # XXX: Dave, check if this test is needed
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular') and int(i['style']) == 'normal':
                have = True

        self.assertTrue(have)


    def test_metadata_wight_in_range(self):
        """ Font weight should be in range from 100 to 900 """
        rcheck = lambda x: True if x>100 and x<900 else False
        self.assertTrue(all([rcheck(x) for x in self.metadata['fonts']]))


    styles = ['Thin', 'ThinItalic', 'ExtraLight',
        'ExtraLightItalic', 'Light', 'LightItalic', 'Regular', 'Italic',
        'Medium', 'MediumItalic', 'SemiBold', 'SemiBoldItalic', 'Bold',
        'BoldItalic', 'ExtraBold', 'ExtraBoldItalic', 'Black', 'BlackItalic']

    def test_metadata_styles_are_canonical(self):
        """ List of alowed styles are: 'Thin', 'ThinItalic', 'ExtraLight',
        'ExtraLightItalic', 'Light', 'LightItalic', 'Regular', 'Italic',
        'Medium', 'MediumItalic', 'SemiBold', 'SemiBoldItalic', 'Bold',
        'BoldItalic', 'ExtraBold', 'ExtraBoldItalic', 'Black', 'BlackItalic' """

        self.assertTrue(all([any([x['postScriptName'].endswith(i) for i in self.styles]) for x in self.metadata['fonts']]))

    def test_font_weight_is_canonical(self):
        """ Font wight property is from canonical styles list"""
        self.assertIn(self.font.weight, self.styles)

    def test_font_name_canonical(self):
        """ Font name is canonical """
        self.assertTrue(any([self.font.fontname.endswith(x) for x in self.styles]))

    def test_font_file_name_canonical(self):
        """ Font name is canonical """
        name = os.path.basename(self.path)


        self.assertTrue(any([self.font.fontname.endswith(x) for x in self.styles]))



