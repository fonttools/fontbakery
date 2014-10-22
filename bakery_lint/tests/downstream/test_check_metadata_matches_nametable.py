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


class CheckMetadataMatchesNameTable(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_metadata_matches_nametable(self):
        """ Metadata key-value match to table name fields """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            report = '%s: Family name was supposed to be "%s" but is "%s"'
            report = report % (font_metadata.name, fm.name,
                               ttfont.familyname)
            self.assertEqual(ttfont.familyname, fm.name, report)
            self.assertEqual(ttfont.fullname, font_metadata.full_name)
