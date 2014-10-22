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
from bakery_lint.base import BakeryTestCase as TestCase
from bakery_lint.metadata import Metadata
from bakery_cli.ttfont import Font


class CheckMenuSubsetContainsProperGlyphs(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_menu_contains_proper_glyphs(self):
        """ Check menu file contains proper glyphs """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            tf = Font.get_ttfont_from_metadata(self.operator.path, font_metadata, is_menu=True)
            self.check_retrieve_glyphs(tf, font_metadata)

    def check_retrieve_glyphs(self, ttfont, font_metadata):
        cmap = ttfont.retrieve_cmap_format_4()

        glyphs = cmap.cmap

        missing_glyphs = set()
        if ord(' ') not in glyphs:
            missing_glyphs.add(' ')

        for g in font_metadata.name:
            if ord(g) not in glyphs:
                missing_glyphs.add(g)

        if missing_glyphs:
            _ = '%s: Menu is missing glyphs: "%s"'
            report = _ % (font_metadata.filename, ''.join(missing_glyphs))
            self.fail(report)
