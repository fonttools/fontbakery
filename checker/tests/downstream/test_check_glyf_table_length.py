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
from cli.ttfont import Font


class CheckGlyfTableLength(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_check_glyf_table_length(self):
        """ Check if there is unused data at the end of the glyf table """
        font = Font.get_ttfont(self.path)

        expected = font.get_loca_length()
        actual = font.get_glyf_length()
        diff = actual - expected

        # allow up to 3 bytes of padding
        if diff > 3:
            _ = ("Glyf table has unreachable data at the end of the table."
                 " Expected glyf table length %s (from loca table), got length"
                 " %s (difference: %s)") % (expected, actual, diff)
            self.fail(_)
        elif diff < 0:
            _ = ("Loca table references data beyond the end of the glyf table."
                 " Expected glyf table length %s (from loca table), got length"
                 " %s (difference: %s)") % (expected, actual, diff)
            self.fail(_)
