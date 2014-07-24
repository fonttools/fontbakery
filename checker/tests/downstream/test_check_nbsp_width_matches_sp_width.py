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
from checker.base import BakeryTestCase as TestCase, tags
from checker.metadata import Metadata
from cli.ttfont import Font


class CheckNbspWidthMatchesSpWidth(TestCase):

    targets = ['metadata']
    path = '.'
    tool = 'lint'
    name = __name__

    def read_metadata_contents(self):
        return open(self.path).read()

    @tags('required')
    def test_check_nbsp_width_matches_sp_width(self):
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            tf = Font.get_ttfont_from_metadata(self.path, font_metadata)
            space_advance_width = tf.advance_width('space')
            nbsp_advance_width = tf.advance_width('uni00A0')

            _ = "%s: The font does not contain a sp glyph"
            self.assertTrue(space_advance_width, _ % font_metadata.filename)
            _ = "%s: The font does not contain a nbsp glyph"
            self.assertTrue(nbsp_advance_width, _ % font_metadata.filename)

            _ = ("%s: The nbsp advance width does not match "
                 "the sp advance width") % font_metadata.filename
            self.assertEqual(space_advance_width, nbsp_advance_width, _)
