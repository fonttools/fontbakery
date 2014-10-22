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
from fontTools import ttLib


class TestKerningPairs(TestCase):

    targets = 'result'
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        ttf = ttLib.TTFont(cls.operator.path)
        return 'kern' not in ttf

    @tags("info")
    def test_kerning_pairs(self):
        """ Number of kerning pairs? """
        ttf = ttLib.TTFont(self.operator.path)
        glyphs = len(ttf['glyf'].glyphs)
        kerningpairs = len(ttf['kern'].kernTables[0].kernTable.keys())
        msg = "Kerning pairs to total glyphs is {0}:{1}"
        self.fail(msg.format(glyphs, kerningpairs))
