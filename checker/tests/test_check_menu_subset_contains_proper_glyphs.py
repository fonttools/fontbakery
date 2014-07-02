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
from fontTools.ttLib import TTFont


class CheckMenuSubsetContainsProperGlyphs(TestCase):

    targets = ['metadata']
    path = '.'
    name = __name__
    tool = 'lint'

    def test_check_menu_subset_contains_proper_glyphs(self):
        fm = Metadata.get_family_metadata(open(self.path).read())
        for font_metadata in fm.fonts:
            menu = op.join(op.dirname(self.path),
                           font_metadata.filename.replace('.ttf', '.menu'))

            if not op.exists(menu):
                print menu
                continue

            self.check_retrieve_glyphs(TTFont(menu), font_metadata)

    def check_retrieve_glyphs(self, ttfont, font_metadata):
        cmap = self.retrieve_cmap_format_4(ttfont)

        missing_glyphs = set()
        if ord(' ') not in cmap.cmap:
            missing_glyphs.add(' ')

        for g in font_metadata.name:
            if ord(g) not in cmap.cmap:
                missing_glyphs.add(g)

        if missing_glyphs:
            _ = '%s: Menu is missing glyphs: "%s"'
            report = _ % (font_metadata.filename, ''.join(missing_glyphs))
            self.fail(report)

    def retrieve_cmap_format_4(self, ttfont):
        for cmap in ttfont['cmap'].tables:
            if cmap.format == 4:
                return cmap
