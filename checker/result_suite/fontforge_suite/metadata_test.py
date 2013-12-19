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
        self.assertEqual(self.font.familyname, self.metadata.get('name', None))

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

        rcheck = lambda x: True if x in range(100, 1000, 100) else False
        self.assertTrue(all([rcheck(x) for x in self.metadata['fonts']]))

    styles = ['Thin', 'ThinItalic', 'ExtraLight',
        'ExtraLightItalic', 'Light', 'LightItalic', 'Regular', 'Italic',
        'Medium', 'MediumItalic', 'SemiBold', 'SemiBoldItalic', 'Bold',
        'BoldItalic', 'ExtraBold', 'ExtraBoldItalic', 'Black', 'BlackItalic']

    italic_styles = ['ThinItalic', 'ExtraLightItalic', 'LightItalic', 'Italic',
        'MediumItalic', 'SemiBoldItalic', 'BoldItalic', 'ExtraBoldItalic',  'BlackItalic']


    # test each key for font item:
    # {
    #   "name": "Merritest", --- doesn't incule style name
    #   "postScriptName": "Merritest-Bold", ---
    #   "fullName": "Merritest Bold", ---
    #   "style": "normal",
    #   "weight": 700,
    #   "filename": "Merritest-Bold.ttf", ---
    #   "copyright": "Merriweather is a medium contrast semi condesed typeface designed to be readable at very small sizes. Merriweather is traditional in feeling despite a the modern shapes it has adopted for screens."
    # },

    def test_metadata_fonts_exists(self):
        """ METADATA.json font propery should exists """
        self.assertTrue(self.metadata.get('fonts', False))

    def test_metadata_fonts_list(self):
        """ METADATA.json font propery should be list """
        self.assertEqual(type(self.metadata.get('fonts', False)), type([]))

    def test_metadata_fonts_fields(self):
        """ METADATA.json "fonts" property items should have "name", "postScriptName",
        "fullName", "style", "weight", "filename", "copyright" keys """
        keys = ["name", "postScriptName",  "fullName", "style", "weight",
            "filename", "copyright"]
        for x in self.metadata.get("fonts", None):
            for j in keys:
                self.assertTrue(j in x)

    def test_metadata_font_name_canonical(self):
        """ METADATA.json fonts 'name' property should be same as font familyname """
        self.assertTrue(all([ x['name'] == self.font.familyname for x in self.metadata.get('fonts', None)]))

    def test_metadata_postscript_canonical(self):
        """ METADATA.json fonts postScriptName should be [font familyname]-[style].
        Alowed styles are: 'Thin', 'ThinItalic', 'ExtraLight', 'ExtraLightItalic',
        'Light', 'LightItalic', 'Regular', 'Italic', 'Medium', 'MediumItalic',
        'SemiBold', 'SemiBoldItalic', 'Bold', 'BoldItalic', 'ExtraBold',
        'ExtraBoldItalic', 'Black', 'BlackItalic' """
        self.assertTrue(all(
             [any([x['postScriptName'].endswith("-"+i) for i in self.styles]) for x in self.metadata.get('fonts', None)]
             ))

    def test_metadata_font_fullname_canonical(self):
        """ METADATA.json fonts fullName property should be '[font.familyname] [font.style]' format (w/o quotes)"""
        for x in self.metadata.get("fonts", None):
            style = None
            fn = x.get('fullName', None)
            for i in self.styles:
                if fn.endswith(i):
                    style = i
                    break
            self.assertTrue(style)
            self.assertEqual("%s %s" % (self.font.familyname, style), fn)

    def test_metadata_font_filename_canonical(self):
        """ METADATA.json fonts filename property should be [font.familyname]-[font.style].ttf format."""
        for x in self.metadata.get("fonts", None):
            style = None
            fn = x.get('filename', None)
            for i in self.styles:
                if fn.endswith("-%s.ttf" % i):
                    style = i
                    break
            self.assertTrue(style)
            self.assertEqual("%s-%s.ttf" % (self.font.familyname, style), fn)

    def test_metadata_fonts_no_dupes(self):
        """ METADATA.json fonts propery only should have uniq values """
        fonts = {}
        for x in self.metadata.get('fonts', None):
            self.assertFalse(x.get('fullName', '') in fonts)
            fonts[x.get('fullName', '')] = x

        self.assertEqual(len(set(fonts.keys())), len(self.metadata.get('fonts', None)))

    def test_metadata_contains_current_font(self):
        """ METADATA.json should contains testing font, under canonic name"""
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break

        self.assertTrue(font)

    # def extract_style(in, )
    def test_metadata_font_style_same_all_fields(self):
        """ METADATA.json fonts properties "name" "postScriptName" "fullName"
        "filename" should have the same style """
        style = None
        # for x in self.metadata.get('fonts', None):
        #     name_style =
        #

    # import magic
    # m = magic.open(magic.MAGIC_MIME)
    # m.load()
    # m.file("/tmp/document.pdf")

    def test_metadata_font_style_italic_correct(self):
        """ METADATA.json fonts style property should be italic if font is italic."""
        self.assertTrue(all(
             [any([x['postScriptName'].endswith("-"+i) for i in self.styles]) for x in self.metadata.get('fonts', None)]
             ))

        for x in self.metadata.get('fonts', None):
            # for i in
            self.assertTrue(x.get('style'))
            if x.get('fullName', None) == current_font:
                font = x
                break
        self.assertTrue(font)
        if int(self.font.italicangle) == 0:
            self.assertEqual(font.get('style', None), 'normal')
        else:
            self.assertEqual(font.get('style', None), 'italic')

    def test_metadata_font_style_italic_follow_internal_data(self):
        """ METADATA.json fonts style property should be italic if font is italic."""
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break
        self.assertTrue(font)
        if int(self.font.italicangle) == 0:
            self.assertEqual(font.get('style', None), 'normal')
        else:
            self.assertEqual(font.get('style', None), 'italic')


    def test_font_weight_is_canonical(self):
        """ Font wight property is from canonical styles list"""
        self.assertIn(self.font.weight, self.styles)

    def test_font_name_canonical(self):
        """ Font name is canonical """
        self.assertTrue(any([self.font.fontname.endswith(x) for x in self.styles]))

    def test_font_file_name_canonical(self):
        """ Font name is canonical """
        name = os.path.basename(self.path)
        canonic_name = "%s-%s.ttf" % (self.font.familyname, self.font.weight)
        self.assertEqual(name, canonic_name)

    def test_menu_file_exists(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(os.path.exists("%s.menu" % os.path.splitext(self.path)[0]))

    def test_menu_file_is_canonical(self):
        """ Menu file should be [font.familyname]-[font.weight].menu """
        name = "%s.menu" % os.path.splitext(self.path)[0]
        canonic_name = "%s-%s.menu" % (self.font.familyname, self.font.weight)
        self.assertEqual(name, canonic_name)

    def test_menu_file_readeable(self):
        """ Menu file should be true ttf file """
        name = "%s.menu" % os.path.splitext(self.path)[0]
        try:
            menu = fontforge.open(name)
        except:
            menu = False

        self.assertTrue(menu)


    def test_metadata_have_subset(self):
        """ METADATA.json shoyld have 'subsets' property """
        self.assertTrue(self.metadata.get('subsets', None))

    subset_list = ['menu', 'latin', 'latin_ext', 'vietnamese', 'greek',
        'cyrillic', 'cyrillic_ext', 'arabic']

    def test_metadata_subsets_names_are_correct(self):
        """ METADATA.json 'subset' property can have only allowed values from list:
        ['menu', 'latin','latin_ext', 'vietnamese', 'greek', 'cyrillic',
        'cyrillic_ext', 'arabic'] """
        self.assertTrue(all([x in self.subset_list for x in self.metadata.get('subsets', None)]))

    def test_subsets_file_are_readable(self):
        """ Each subset file should be correct binary files """
        result = []
        for x in self.metadata.get('subsets', None):
            name = "%s.%s" % (os.path.splitext(self.path)[0], x)
            try:
                menu = fontforge.open(name)
                flag = True
            except EnvironmentError:
                flag = False
            result.append(flag)
        self.assertTrue(all(result))

    # def test_menu_have_chars(self):
    #     """ Test does .menu file have chars needed for METADATA family key """
    #     from checker.tools import combine_subsets
    #     result = []
    #     for x in self.metadata.get('subsets', None):
    #         name = "%s.%s" % (os.path.splitext(self.path)[0], x)

    #         menu = fontforge.open(name)

    #     self.assertTrue(all([ x in menu for x in result]))

    def test_metadata_subsets_files(self):
        """ Check that METADATA subsets values have corresponding subset files on disk """
        name = "%s.menu" % os.path.splitext(self.path)[0]
        self.assertTrue(
            all(
                [os.path.exists("%s.%s" % (name, x)) for x in self.metadata['subsets'] ]
                )
        )

    # def test_metadata_family_match_filename(self):
    #     """ Check that METADATA family value matches font filenames """

    # def test_metadata_value_match_font_weight(self):
    #     """Check that METADATA font.weight keys match font internal metadata"""
    #     raise NotImplementedError

    # def test_metadata_style_match_internal_metadata(self):
    #     """Check that METADATA font.style keys match font internal metadata (including MacStyle)"""
    #     raise NotImplementedError

    # def test_metadata_(self):
    #     """Check that subset files filesize is smaller than ttf original"""
    #     raise NotImplementedError

    # def test_metadata_(self):
    #     """Check that the family name matches the font name"""
    #     raise NotImplementedError

    def test_em_is_1000(self):
        """ Font em should be equal 1000 """
        self.assertEqual(self.font.em, 1000)


# 'Thin', 100
# 'ThinItalic', 100
# 'ExtraLight', 200
# 'ExtraLightItalic', 200
# 'Light', 300
# 'LightItalic', 300
# 'Regular', 400
# 'Italic', 400
# 'Medium', 500
# 'MediumItalic', 500
# 'SemiBold', 600
# 'SemiBoldItalic', 600
# 'Bold', 700
# 'BoldItalic', 700
# 'ExtraBold', 800
# 'ExtraBoldItalic', 800
# 'Black', 900
# 'BlackItalic', 900
