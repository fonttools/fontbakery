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
import os

from checker.base import BakeryTestCase as TestCase
from checker.metadata import Metadata


class CheckCanonicalFilenames(TestCase):
    weights = {
        100: 'Thin',
        200: 'ExtraLight',
        300: 'Light',
        400: '',
        500: 'Medium',
        600: 'SemiBold',
        700: 'Bold',
        800: 'ExtraBold',
        900: 'Black'
    }

    style_names = {
        'normal': '',
        'italic': 'Italic'
    }

    path = '.'
    name = __name__
    tool = 'Lint'
    targets = ['metadata']

    def test_check_canonical_filenames(self):
        """ Test If filename is canonical """
        family_metadata = Metadata.get_family_metadata(open(self.path).read())
        for font_metadata in family_metadata.fonts:
            canonical_filename = self.create_canonical_filename(font_metadata)
            # try to open file
            open(os.path.join(os.path.dirname(self.path),
                              font_metadata.filename))
            self.assertEqual(canonical_filename, font_metadata.filename)

    def create_canonical_filename(self, font_metadata):
        familyname = font_metadata.name.replace(' ', '')
        style_weight = '%s%s' % (self.weights.get(font_metadata.weight),
                                 self.style_names.get(font_metadata.style))
        if not style_weight:
            style_weight = 'Regular'
        return '%s-%s.ttf' % (familyname, style_weight)
