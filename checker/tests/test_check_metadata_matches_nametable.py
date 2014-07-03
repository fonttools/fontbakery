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
from checker.metadata import Metadata
from checker.ttfont import Font


class CheckMetadataMatchesNameTable(TestCase):

    path = '.'
    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_check_metadata_matches_nametable(self):
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            ttfont = Font.get_ttfont(self.path, font_metadata)
            familyname_from_font = self.find_familyname_in_nametable(ttfont)

            report = '%s: Family name was supposed to be "%s" but is "%s"'
            report = report % (font_metadata.name, fm.name,
                               familyname_from_font)
            self.assertEqual(familyname_from_font, fm.name, report)
