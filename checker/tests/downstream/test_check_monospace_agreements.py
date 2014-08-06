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
from checker.metadata import Metadata
from cli.ttfont import Font


class CheckMonospaceAgreement(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_check_monospace_agreement(self):
        """ Monospace font has hhea.advanceWidthMax equal to each
            glyph advanceWidth """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        if fm.category != 'Monospace':
            return
        for font_metadata in fm.fonts:
            font = Font.get_ttfont_from_metadata(self.path,
                                                 font_metadata.filename)
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    self.fail(('Glyph advanceWidth must be same'
                               ' across all glyphs %s' % prev))
                prev = font.advance_width(g)

            if prev != font.advance_width():
                msg = ('"hhea" table advanceWidthMax property differs'
                       ' to glyphs advanceWidth [%s, %s]')
                self.fail(msg % (prev, font.advance_width()))
