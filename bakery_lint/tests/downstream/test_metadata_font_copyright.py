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
from bakery_lint.base import BakeryTestCase as TestCase, tags
from bakery_lint.metadata import Metadata


class CheckMetadataContainsReservedFontName(TestCase):

    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required', 'info')
    def test_copyright_contains_correct_rfn(self):
        """ Copyright string contains "Reserved File Name" """
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

    @tags('required')
    def test_copyright_is_consistent_across_family(self):
        """ METADATA.json fonts copyright string is the same for all items """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        copyright = ''
        for font_metadata in fm.fonts:
            if copyright and font_metadata.copyright != copyright:
                self.fail('Copyright is inconsistent across family')
            copyright = font_metadata.copyright

    @tags('required')
    def test_metadata_copyright_size(self):
        """ Copyright string should be less than 500 chars """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            self.assertLessEqual(len(font_metadata.copyright), 500)
