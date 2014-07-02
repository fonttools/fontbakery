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


class CheckCanonicalWeights(TestCase):

    path = '.'
    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def test_check_canonical_weights(self):
        fm = Metadata.get_family_metadata(open(self.path).read())
        for font_metadata in fm.fonts:
            weight = font_metadata.weight
            first_digit = weight / 100
            is_invalid = (weight % 100) != 0 or (first_digit < 1
                                                 or first_digit > 9)
            _ = ("%s: The weight is %d which is not a "
                 "multiple of 100 between 1 and 9")

            self.assertFalse(is_invalid, _ % (op.basename(self.path),
                                              font_metadata.weight))

            tf = TTFont(op.join(op.dirname(self.path), font_metadata.filename))
            _ = ("%s: METADATA.json overwrites the weight. "
                 " The METADATA.json weight is %d and the font"
                 " file %s weight is %d")
            _ = _ % (font_metadata.filename, font_metadata.weight,
                     font_metadata.filename, tf['OS/2'].usWeightClass)

            self.assertEqual(tf['OS/2'].usWeightClass, font_metadata.weight)
