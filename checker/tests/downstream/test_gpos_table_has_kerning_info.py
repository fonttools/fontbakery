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


class CheckGposTableHasKerningInfo(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_gpos_table_has_kerning_info(self):
        """ GPOS table has kerning information """
        font = Font.get_ttfont(self.path)

        try:
            font['GPOS']
        except KeyError:
            self.fail('"GPOS" does not exist in font')
        flaglookup = False
        for lookup in font['GPOS'].table.LookupList.Lookup:
            if lookup.LookupType == 2:  # Adjust position of a pair of glyphs
                flaglookup = lookup
                break  # break for..loop to avoid reading all kerning info
        self.assertTrue(flaglookup, msg='GPOS doesnt have kerning information')
        self.assertGreater(flaglookup.SubTableCount, 0)
        self.assertGreater(flaglookup.SubTable[0].PairSetCount, 0)
