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
import os.path as op

from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font
from cli.utils import UpstreamDirectory


class FontTestPrepolation(TestCase):

    path = '.'
    name = __name__
    targets = ['upstream-repo']
    tool = 'lint'

    def get_ufo_glyphs(self, path):
        f = fontforge.open(op.join(self.path, path))
        return [g.glyphname for g in f.glyphs()]

    def get_ttf_glyphs(self, path):
        f = Font.get_ttfont(op.join(self.path, path))
        return [g for g in f.getGlyphOrder()]

    def test_font_test_prepolation_glyph_names(self):
        """ Check glyph names are all the same across family """
        directory = UpstreamDirectory(self.path)

        glyphs = []
        for f in directory.get_fonts():
            if f[-4:] in ['.ufo', '.sfd']:
                glyphs_ = self.get_ufo_glyphs()
            else:
                glyphs_ = self.get_ttf_glyphs()

            if glyphs and glyphs != glyphs_:
                self.fail('Family has different glyphs across fonts')
