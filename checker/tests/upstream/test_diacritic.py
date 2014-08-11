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
from cli.pifont import PiFont
from cli.utils import UpstreamDirectory


class TestDiacritic(TestCase):
    """ These tests are using text file with contents of diacritics glyphs """

    path = '.'
    targets = ['upstream-repo']
    tool = 'lint'
    name = __name__

    def setUp(self):
        path = op.realpath(op.dirname(__file__))
        content = open(op.join(path, 'diacritics.txt')).read()
        self.diacriticglyphs = [x for x in content.split() if x.strip()]
        self.directory = UpstreamDirectory(self.path)

    def is_diacritic(self, glyphname):
        for diacriticglyph in self.diacriticglyphs:
            if glyphname.index(glyphname) >= 1:
                return True

    def filter_diacritics_glyphs(self):
        diacritic_glyphs = []
        for filepath in self.directory.UFO:
            pifont = PiFont(op.join(self.path, filepath))
            for glyphcode, glyphname in pifont.get_glyphs():

                if not self.is_diacritic(glyphname):
                    continue

                diacritic_glyphs.append(pifont.get_glyph(glyphname))
        return diacritic_glyphs

    def test_diacritic_made_as_own_glyphs(self):
        diacritic_glyphs = self.filter_diacritics_glyphs()

        flatglyphs = 0
        for glyph in diacritic_glyphs:
            if glyph.components:
                # compositeglyphs += 1
                pass
            elif glyph.anchors:
                # markglyphs += 1
                pass
            elif glyph.contours:
                flatglyphs += 1

        if flatglyphs and len(diacritic_glyphs) != flatglyphs:
            percentage = flatglyphs / len(diacritic_glyphs)
            self.fail('%s%% are made by Flat' % percentage)

    def test_diacritic_made_as_component(self):
        pass

    def test_diacritic_made_as_mark_to_mark(self):
        pass
