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
import lxml.etree
import os
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
        try:
            f = Font.get_ttfont(op.join(self.path, path))
        except Exception, ex:
            self.fail('%s: %s' % (ex, path))
        return [g for g in f.ttfont.getGlyphOrder()]

    def test_font_test_prepolation_glyph_names(self):
        """ Check glyph names are all the same across family """
        directory = UpstreamDirectory(self.path)

        glyphs = []
        for f in directory.get_fonts():
            glyphs_ = self.get_glyphs(f)

            if glyphs and glyphs != glyphs_:
                self.fail('Family has different glyphs across fonts')

    def get_glyphs(self, f):
        if f[-4:] in ['.ufo', '.sfd']:
            return self.get_ufo_glyphs(f)
        return self.get_ttf_glyphs(f)

    def get_contours(self, f, g):
        file_extension = f[-4:]
        if file_extension == '.ufo':
            for k in os.listdir(op.join(self.path, f, 'glyphs')):
                doc = lxml.etree.parse(op.join(self.path, f, 'glyphs', k))
                if not doc.xpath('//glyph[@name="%s"]' % g):
                    continue

                value = len(doc.xpath('//outline/contour'))

                components = doc.xpath('//outline/component/@base')
                for component in components:
                    value += self.get_contours(f, component)

                return value

        if file_extension in ['.ttf', '.ttx', '.otf']:
            pass

    def test_font_prepolation_glyph_contours(self):
        """ Check that glyphs has same number of contours across family """
        directory = UpstreamDirectory(self.path)

        glyphs = {}
        for f in directory.get_fonts():
            glyphs_ = self.get_glyphs(f)

            for g in glyphs_:
                number_contours = self.get_contours(f, g)
                if g in glyphs and glyphs[g] != number_contours:
                    msg = ('Number of contours of glyph "%s" does not match'
                           'Expected %s contours, but actual is %s contours')
                    self.fail(msg % (g, glyphs[g], number_contours))
                glyphs[g] = number_contours
