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
import yaml
import os
import magic

from checker.base import BakeryTestCase as TestCase, tags


class MetadataJSONTest(TestCase):
    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'
    longMessage = True

    def setUp(self):
        self.font = fontforge.open(self.path)
        medatata_path = os.path.join(os.path.dirname(self.path),
                                     'METADATA.json')
        self.metadata = yaml.load(open(medatata_path, 'r').read())
        self.fname = os.path.splitext(self.path)[0]
        self.root_dir = os.path.dirname(self.path)

    def test_family_is_listed_in_gwf(self):
        """ Fontfamily is listed in Google Font Directory """
        import requests
        url = 'http://fonts.googleapis.com/css?family=%s' % self.metadata['name'].replace(' ', '+')
        fp = requests.get(url)
        self.assertTrue(fp.status_code == 200, 'No family found in GWF in %s' % url)
        self.assertEqual(self.metadata.get('visibility'), 'External')

    def test_metadata_family_values_are_all_the_same(self):
        """ Check that METADATA family values are all the same """
        families_names = set([x['name'] for x in self.metadata.get('fonts')])
        self.assertEqual(len(set(families_names)), 1)

    @tags('required',)
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

    @tags('required',)
    def test_metadata_regular_is_400(self):
        """ Usually Regular should be 400 """
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular') \
                    and int(i.get('weight', 0)) == 400:
                have = True

        self.assertTrue(have)

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        have = False
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', '').endswith('Regular') \
                    and x.get('style', '') == 'normal':
                have = True
        self.assertTrue(have)

    def test_metadata_fonts_exists(self):
        """ METADATA.json font propery should exists """
        self.assertTrue(self.metadata.get('fonts', False))

    def test_metadata_fonts_list(self):
        """ METADATA.json font propery should be list """
        self.assertEqual(type(self.metadata.get('fonts', False)), type([]))

    def test_metadata_font_name_canonical(self):
        """ METADATA.json fonts 'name' property should be
            same as font familyname """
        self.assertTrue(all([x['name'] == self.font.familyname
                             for x in self.metadata.get('fonts', None)]))

    @tags('required')
    def test_metadata_filename_matches_postScriptName(self):
        """ METADATA.json `filename` is matched to `postScriptName`
            property """
        for x in self.metadata.get("fonts", None):
            post_script_name = x.get('postScriptName', '')
            filename = x.get('filename', '')
            self.assertEqual(os.path.splitext(filename)[0], post_script_name)

    @tags('required')
    def test_metadata_fullname_matches_postScriptName(self):
        """ METADATA.json `fullName` is matched to `postScriptName`
            property """
        for x in self.metadata.get("fonts", None):
            post_script_name = x.get('postScriptName', '').replace('-', ' ')
            fullname = x.get('fullName', '')
            self.assertEqual(fullname, post_script_name)

    @tags('required')
    def test_metadata_postScriptName_matches_internal_fontname(self):
        """ Checks that METADATA.json 'postScriptName' value matches
            font internal 'fontname' metadata """
        for font in self.metadata.get('fonts', []):
            if font['filename'] != os.path.basename(self.fname):
                continue
            self.assertEqual(font['postScriptName'], self.font.fontname)

    @tags('required')
    def test_metadata_postScriptName_matches_font_filename(self):
        """ Checks that METADATA.json 'postScriptName' value matches
            font internal 'fontname' metadata """
        for font in self.metadata.get('fonts', []):
            font_filename = os.path.basename(self.fname)
            if font['filename'] == font_filename:
                continue
            self.assertEqual(font['postScriptName'],
                             os.path.splitext(font_filename)[0])

    def test_metadata_fonts_no_dupes(self):
        """ METADATA.json fonts propery only should have uniq values """
        fonts = {}
        for x in self.metadata.get('fonts', None):
            self.assertFalse(x.get('fullName', '') in fonts)
            fonts[x.get('fullName', '')] = x

        self.assertEqual(len(set(fonts.keys())),
                         len(self.metadata.get('fonts', None)))

    def test_metadata_contains_current_font(self):
        """ METADATA.json should contains testing font, under canonic name"""
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break

        self.assertTrue(font)

    def test_metadata_fullname_is_equal_to_internal_font_fullname(self):
        """ METADATA.json 'fullname' value matches internal 'fullname' """
        metadata_fullname = ''
        for font in self.metadata.get('fonts', []):
            if font['filename'] == os.path.basename(self.path):
                metadata_fullname = font['fullName']
                break
        self.assertEqual(self.font.fullname, metadata_fullname)

    def test_metadata_fonts_fields_have_fontname(self):
        """ METADATA.json fonts items fields "name", "postScriptName",
            "fullName", "filename" contains font name right format """
        for x in self.metadata.get('fonts', None):
            self.assertIn(self.font.familyname, x.get('name', ''))
            self.assertIn(self.font.familyname, x.get('fullName', ''))
            self.assertIn("".join(str(self.font.familyname).split()),
                          x.get('filename', ''))
            self.assertIn("".join(str(self.font.familyname).split()),
                          x.get('postScriptName', ''))

    def test_metadata_have_subset(self):
        """ METADATA.json shoyld have 'subsets' property """
        self.assertTrue(self.metadata.get('subsets', None))

    # VV TODO: Subset list must be selected from pyFontaine
    subset_list = ['menu', 'latin', 'latin_ext', 'vietnamese', 'greek',
                   'cyrillic', 'cyrillic_ext', 'arabic']

    def test_metadata_subsets_names_are_correct(self):
        """ METADATA.json 'subset' property can have only allowed values
            from list: ['menu', 'latin','latin_ext', 'vietnamese', 'greek',
            'cyrillic', 'cyrillic_ext', 'arabic'] """
        self.assertTrue(all([x in self.subset_list
                             for x in self.metadata.get('subsets', None)]))

    @tags('required')
    def test_metadata_keys(self):
        """ METADATA.json should have top keys: ["name", "designer",
            "license", "visibility", "category", "size", "dateAdded",
            "fonts", "subsets"] """

        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]

        for x in top_keys:
            self.assertIn(x, self.metadata, msg="Missing %s key" % x)

    @tags('required')
    def test_metadata_designer_exists_in_profiles_csv(self):
        """ Designer exists in GWF profiles.csv """
        designer = self.metadata.get('designer', '')
        self.assertTrue(designer)
        import urllib
        import csv
        fp = urllib.urlopen('https://googlefontdirectory.googlecode.com/hg/designers/profiles.csv')
        try:
            designers = []
            for row in csv.reader(fp):
                if not row:
                    continue
                designers.append(row[0])
            self.assertTrue(designer in designers,
                            msg='Designer %s is not in profiles.csv' % designer)
        except Exception:
            self.assertTrue(False)

    @tags('required')
    def test_metadata_fonts_key_list(self):
        """ METADATA.json font key should be list """
        self.assertEqual(type(self.metadata.get('fonts', '')), type([]))

    @tags('required')
    def test_metadata_subsets_key_list(self):
        """ METADATA.json subsets key should be list """
        self.assertEqual(type(self.metadata.get('subsets', '')), type([]))

    @tags('required')
    def test_subsets_files_is_font(self):
        """ Subset file is a TrueType format """
        for subset in self.metadata.get('subsets', []):
            self.assertTrue(magic.from_file(self.fname + '.' + subset),
                            'TrueType font data')

    @tags('required')
    def test_metadata_fonts_items_dicts(self):
        """ METADATA.json fonts key items are dicts """
        for x in self.metadata.get('fonts', None):
            self.assertEqual(type(x), type({}), msg="type(%s) is not dict" % x)

    @tags('required')
    def test_metadata_subsets_items_string(self):
        """ METADATA.json subsets key items are strings """
        for x in self.metadata.get('subsets', None):
            self.assertEqual(type(x), type(""), msg="type(%s) is not dict" % x)

    @tags('required')
    def test_metadata_top_keys_types(self):
        """ METADATA.json should have proper top keys types """
        self.assertEqual(type(self.metadata.get("name", None)),
                         type(""), msg="name key type invalid")
        self.assertEqual(type(self.metadata.get("designer", None)),
                         type(""), msg="designer key type invalid")
        self.assertEqual(type(self.metadata.get("license", None)),
                         type(""), msg="license key type invalid")
        self.assertEqual(type(self.metadata.get("visibility", None)),
                         type(""), msg="visibility key type invalid")
        self.assertEqual(type(self.metadata.get("category", None)),
                         type(""), msg="category key type invalid")
        self.assertEqual(type(self.metadata.get("size", None)),
                         type(0), msg="size key type invalid")
        self.assertEqual(type(self.metadata.get("dateAdded", None)),
                         type(""), msg="dateAdded key type invalid")

    @tags('required')
    def test_metadata_no_unknown_top_keys(self):
        """ METADATA.json don't have unknown top keys """
        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]
        for x in self.metadata.keys():
            self.assertIn(x, top_keys, msg="%s found unknown top key" % x)

    @tags('required')
    def test_metadata_atleast_latin_menu_subsets_exist(self):
        """ METADATA.json subsets should have at least 'menu' and 'latin' """
        self.assertIn('menu', self.metadata.get('subsets', []),
                      msg="Subsets missing menu")
        self.assertIn('latin', self.metadata.get('subsets', []),
                      msg="Subsets missing latin")

    @tags('required')
    def test_metadata_license(self):
        """ METADATA.json license is 'Apache2', 'UFL' or 'OFL' """
        licenses = ['Apache2', 'OFL', 'UFL']
        self.assertIn(self.metadata.get('license', ''), licenses,
                      msg='License has invalid value')

    @tags('required')
    def test_metadata_has_unique_style_weight_pairs(self):
        """ METADATA.json only contains unique style:weight pairs """
        pairs = []
        for fontdata in self.metadata.get('fonts', []):
            styleweight = '%s:%s' % (fontdata['style'],
                                     fontdata.get('weight', 0))
            self.assertNotIn(styleweight, pairs)
            pairs.append(styleweight)
