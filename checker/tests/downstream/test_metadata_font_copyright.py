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


class CheckMetadataContainsReservedFontName(TestCase):

    path = '.'
    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    @tags(['required', 'info'])
    def test_postscriptname_contains_correct_weight(self):
        """ Metadata weight matches postScriptName """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:

            if 'Reserved Font Name' not in font_metadata.copyright:
                msg = '"%s" should have "Reserved File Name"'
                self.fail(msg % font_metadata.copyright)

    @tags('required')
    def test_copyright_matches_pattern(self):
        """ Copyright string matches to Copyright * 20\d\d * (*@*.*) """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            self.assertRegexpMatches(font_metadata.copyright,
                                     r'Copyright\s+\(c\)\s+20\d{2}.*\(.*@.*.*\)')
