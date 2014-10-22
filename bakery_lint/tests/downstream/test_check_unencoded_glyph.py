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
import fontTools.ttLib

from bakery_lint.base import BakeryTestCase as TestCase, tags, autofix
from bakery_cli.scripts import encode_glyphs


class TestFontUnencodedGlyph(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    ttx = None
    unencoded_glyphs = []

    @tags('note')
    @autofix('bakery_cli.pipe.autofix.fix_encode_glyphs')
    def test_font_unencoded_glyphs(self):
        """ Font does not have unencoded glyphs """
        self.ttx = fontTools.ttLib.TTFont(self.operator.path, 0)
        self.unencoded_glyphs = encode_glyphs.get_unencoded_glyphs(self.ttx)
        self.assertIs(self.unencoded_glyphs, [],
                      msg='There should not be unencoded glyphs')
