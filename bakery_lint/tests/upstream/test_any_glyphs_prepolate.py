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

from bakery_lint.base import BakeryTestCase as TestCase
from bakery_cli.pifont import PiFont
from bakery_cli.utils import UpstreamDirectory


class FontTestPrepolation(TestCase):

    name = __name__
    targets = ['upstream-repo']
    tool = 'lint'

    def test_family_glyph_names_match(self):
        """ Each font in family has matching glyph names? """
        directory = UpstreamDirectory(self.operator.path)
        # TODO does this glyphs list object get populated?
        glyphs = []
        for f in directory.get_fonts():
            font = PiFont(op.join(self.operator.path, f))
            glyphs_ = font.get_glyphs()

            if glyphs and glyphs != glyphs_:
                # TODO report which font 
                self.fail('Family has different glyphs across fonts')

    def test_font_prepolation_glyph_contours(self):
        """ Check that glyphs has same number of contours across family """
        directory = UpstreamDirectory(self.operator.path)

        glyphs = {}
        for f in directory.get_fonts():
            font = PiFont(op.join(self.operator.path, f))
            glyphs_ = font.get_glyphs()

            for glyphcode, glyphname in glyphs_:
                contours = font.get_contours_count(glyphname)
                if glyphcode in glyphs and glyphs[glyphcode] != contours:
                    msg = ('Number of contours of glyph "%s" does not match.'
                           ' Expected %s contours, but actual is %s contours')
                    self.fail(msg % (glyphname, glyphs[glyphcode], contours))
                glyphs[glyphcode] = contours

    def test_font_prepolation_glyph_points(self):
        """ Check that glyphs has same number of points across family """
        directory = UpstreamDirectory(self.operator.path)

        glyphs = {}
        for f in directory.get_fonts():
            font = PiFont(op.join(self.operator.path, f))
            glyphs_ = font.get_glyphs()

            for g, glyphname in glyphs_:
                points = font.get_points_count(glyphname)
                if g in glyphs and glyphs[g] != points:
                    msg = ('Number of points of glyph "%s" does not match.'
                           ' Expected %s points, but actual is %s points')
                    self.fail(msg % (glyphname, glyphs[g], points))
                glyphs[g] = points
