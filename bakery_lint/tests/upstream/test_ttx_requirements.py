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
import re

from fontTools.ttLib import TTFont

from bakery_lint.base import BakeryTestCase as TestCase


class SourceTTXTest(TestCase):
    targets = ['upstream-ttx']
    tool = 'fontTools'
    name = __name__

    def setUp(self):
        font = TTFont(None, lazy=False, recalcBBoxes=True,
                      verbose=False, allowVID=False)
        font.importXML(self.operator.path, quiet=True)
        self.font = font

    def test_ttx_duplicate_glyphs(self):
        """ Font contains unique glyph names?
            (Duplicate glyph names prevent font installation on Mac OS X.)
        """
        glyphs = []
        for _, g in enumerate(self.font.getGlyphOrder()):
            self.assertFalse(re.search(r'#\w+$', g),
                             msg="Font contains incorrectly named glyph %s" % g)
            glyphID = re.sub(r'#\w+', '', g)

            # Each GlyphID has to be unique in TTX
            self.assertFalse(glyphID in glyphs,
                             msg="GlyphID %s occurs twice in TTX" % g)
            glyphs.append(glyphs)

    def test_epar_in_keys(self):
        """ EPAR table present in font? """
        self.assertIn('EPAR', self.font.keys(), 'No')
