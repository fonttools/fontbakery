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


class CheckFamilyNameMatchesFontNames(TestCase):

    name = __name__
    path = '.'
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_check_familyname_matches_fontnames(self):
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            _ = '%s: Family name "%s" does not match font name: "%s"'
            _ = _ % (font_metadata.filename, fm.name, font_metadata.name)
            self.assertEqual(font_metadata.name, fm.name, _)
