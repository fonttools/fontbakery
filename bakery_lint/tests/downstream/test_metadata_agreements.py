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
import os

from bakery_lint.base import BakeryTestCase as TestCase, tags
from bakery_lint.metadata import Metadata
from bakery_cli.ttfont import Font


class TestFontOnDiskFamilyEqualToMetadataJSON(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required',)
    def test_font_on_disk_family_equal_in_metadata_json(self):
        """ Font on disk and in METADATA.json have the same family name """
        contents = self.read_metadata_contents()
        metadata = Metadata.get_family_metadata(contents)

        unmatched_fonts = []
        for font_metadata in metadata.fonts:
            try:
                font = Font.get_ttfont_from_metadata(self.operator.path,
                                                     font_metadata)
            except IOError:
                continue
            if font.familyname != font_metadata.name:
                unmatched_fonts.append(font_metadata.filename)

        if unmatched_fonts:
            msg = 'Unmatched family name are in fonts: {}'
            self.fail(msg.format(', '.join(unmatched_fonts)))


class TestPostScriptNameInMetadataEqualFontOnDisk(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required')
    def test_postscriptname_in_metadata_equal_to_font_on_disk(self):
        """ Checks METADATA.json 'postScriptName' matches TTF 'postScriptName' """
        contents = self.read_metadata_contents()
        metadata = Metadata.get_family_metadata(contents)

        for font_metadata in metadata.fonts:
            try:
                font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            except IOError:
                continue
            if font.post_script_name != font_metadata.post_script_name:

                msg = 'In METADATA postScriptName="{0}", but in TTF "{1}"'
                self.fail(msg.format(font.post_script_name,
                                     font_metadata.post_script_name))


class CheckMetadataAgreements(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def setUp(self):
        contents = self.read_metadata_contents()
        self.metadata = Metadata.get_family_metadata(contents)

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_metadata_family_values_are_all_the_same(self):
        """ Check that METADATA family values are all the same """
        name = ''
        for font_metadata in self.metadata.fonts:
            if name and font_metadata.name != name:
                self.fail('Family name in metadata fonts items not the same')
            name = font_metadata.name

    def test_metadata_font_have_regular(self):
        """ According GWF standarts font should have Regular style. """
        # this tests will appear in each font
        have = False
        for i in self.metadata.fonts:
            if i.weight == 400 and i.style == 'normal':
                have = True

        self.assertTrue(have)

    @tags('required')
    def test_metadata_regular_is_400(self):
        """ Regular should be 400 """
        have = False
        for i in self.metadata.fonts:
            if i.filename.endswith('Regular.ttf') and i.weight == 400:
                have = True
        if not have:
            self.fail(('METADATA.json does not contain Regular font. At least'
                       ' one font must be Regular and its weight must be 400'))

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        have = False
        for x in self.metadata.fonts:
            if x.full_name.endswith('Regular') and x.style == 'normal':
                have = True
        self.assertTrue(have)

    @tags('required')
    def test_metadata_filename_matches_postscriptname(self):
        """ METADATA.json `filename` matches `postScriptName` """
        import re
        regex = re.compile(r'\W')

        for x in self.metadata.fonts:
            post_script_name = regex.sub('', x.post_script_name)
            filename = regex.sub('', os.path.splitext(x.filename)[0])
            if filename != post_script_name:
                msg = '"{0}" does not match "{1}"'
                self.fail(msg.format(x.filename, x.post_script_name))

    @tags('required')
    def test_metadata_fullname_matches_postScriptName(self):
        """ METADATA.json `fullName` matches `postScriptName` """
        import re
        regex = re.compile(r'\W')

        for x in self.metadata.fonts:
            post_script_name = regex.sub('', x.post_script_name)
            fullname = regex.sub('', x.full_name)
            if fullname != post_script_name:
                msg = '"{0}" does not match "{1}"'
                self.fail(msg.format(x.full_name, x.post_script_name))

    def test_metadata_fullname_is_equal_to_internal_font_fullname(self):
        """ METADATA.json 'fullname' value matches internal 'fullname' """
        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            self.assertEqual(font.fullname, font_metadata.full_name)

    def test_font_name_matches_family(self):
        """ METADATA.json fonts 'name' property should be
            same as font familyname """

        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if font_metadata.name != font.familyname:
                msg = '"fonts.name" property is not the same as TTF familyname'
                self.fail(msg)

    def test_metadata_fonts_fields_have_fontname(self):
        """ METADATA.json fonts items fields "name", "postScriptName",
            "fullName", "filename" contains font name right format """
        for x in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, x)

            self.assertIn(font.familyname, x.name)
            self.assertIn(font.familyname, x.full_name)
            self.assertIn("".join(str(font.familyname).split()),
                          x.filename)
            self.assertIn("".join(str(font.familyname).split()),
                          x.post_script_name)
