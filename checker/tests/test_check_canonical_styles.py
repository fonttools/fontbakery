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
from fontTools import ttLib


class CheckCanonicalStyles(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    CANONICAL_STYLE_VALUES = ['italic', 'normal']

    def test_check_canonical_styles(self):
        """ Test If font styles are canonical """
        fm = Metadata.get_family_metadata(open(self.path).read())
        for font_metadata in fm.fonts:
            self.assertIn(font_metadata.style, self.CANONICAL_STYLE_VALUES)
            self.check_style_matches_in_fontfile(font_metadata)

    def check_style_matches_in_fontfile(self, font_metadata):
        fontpath = op.join(op.dirname(self.path), font_metadata.filename)
        ttfont = ttLib.TTFont(fontpath)
        is_italic = (ttfont['head'].macStyle & 0b10
                     or ttfont['post'].italicAngle
                     or self.find_italic_in_name_table(ttfont))
        if is_italic:
            if font_metadata.style != 'italic':
                _ = "%s: The font style is %s but it should be italic"
                self.fail(_ % (font_metadata.filename, font_metadata.style))
        else:
            if font_metadata.style != 'normal':
                _ = "%s: The font style is %s but it should be normal"
                self.fail(_ % (font_metadata.filename, font_metadata.style))

    def find_italic_in_name_table(self, ttfont):
        for entry in ttfont['name'].names:
            if 'italic' in self.bin2unistring(entry).lower():
                return True

    def bin2unistring(self, record):
        if b'\000' in record.string:
            string = record.string.decode('utf-16-be')
            return string.encode('utf-8')
        else:
            return record.string
