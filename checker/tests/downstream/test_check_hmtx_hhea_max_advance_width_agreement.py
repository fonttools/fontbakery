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


class CheckHmtxHheaMaxAdvanceWidthAgreement(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_check_hmtx_hhea_max_advance_width_agreement(self):
        """ Check if MaxAdvanceWidth agree in the Hmtx and Hhea tables """
        font = Font.get_ttfont(self.path)

        hmtx_advance_width_max = font.get_hmtx_max_advanced_width()
        hhea_advance_width_max = font.advance_width_max
        error = ("AdvanceWidthMax mismatch: expected %s (from hmtx);"
                 " got %s (from hhea)") % (hmtx_advance_width_max,
                                           hhea_advance_width_max)
        self.assertEqual(hmtx_advance_width_max,
                         hhea_advance_width_max, error)
