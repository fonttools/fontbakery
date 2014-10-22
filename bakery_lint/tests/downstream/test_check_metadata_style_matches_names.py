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
from bakery_lint.base import BakeryTestCase as TestCase
from bakery_lint.metadata import Metadata
from bakery_cli.ttfont import Font


class CheckItalicStyleMatchesMacStyle(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_italic_style_matches_names(self):
        """ Check metadata.json font.style `italic` matches font internal """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

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

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_normal_style_matches_names(self):
        """ Check metadata.json font.style `italic` matches font internal """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

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
