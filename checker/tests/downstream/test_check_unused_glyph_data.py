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
from cli.ttfont import Font


class CheckUnusedGlyphData(TestCase):

    path = '.'
    targets = ['result']
    tool = 'lint'
    name = __name__

    def test_check_unused_glyph_data(self):
        f = Font.get_ttfont(self.path)
        glyf_length = f.get_glyf_length()

        loca_num_glyphs = f.get_loca_num_glyphs()

        last_glyph_offset = f.get_loca_glyph_offset(loca_num_glyphs - 1)
        last_glyph_length = f.get_loca_glyph_length(loca_num_glyphs - 1)

        unused_data = glyf_length - (last_glyph_offset + last_glyph_length)

        error = ("there were %s bytes of unused data at the end"
                 " of the glyf table") % unused_data
        self.assertEqual(unused_data, 0, error)
