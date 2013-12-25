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
from fontTools import ttLib
import yaml
import os
import magic

class FontToolsTest(TestCase):
    targets = ['result']
    tool   = 'FontTools'
    name   = __name__
    path   = '.'

    def setUp(self):
        self.font = ttLib.TTFont(self.path)


    def test_dev(self):
        """ Test """
        import ipdb; ipdb.set_trace()


    def test_tables(self):
        """ List of tables that shoud be in font file """
        # xen: actually I take this list from most popular open font Open Sans,
        # belive that it is most mature.
        # This list should be reviewed
        tables = ['GlyphOrder', 'head', 'hhea', 'maxp', 'OS/2', 'hmtx',
            'cmap', 'fpgm', 'prep', 'cvt ', 'loca', 'glyf', 'name', # 'kern',
            'post', 'gasp', 'GDEF', 'GPOS', 'GSUB', 'DSIG']

        for x in self.font.keys():
            self.assertIn(x, tables, msg="%s table not found in table list" % x)


    def test_tables_no_kern(self):
        """ Check that no KERN table exists """
        self.assertNotIn('kern', self.font.keys())


    def test_table_gasp_type(self):
        """ Font table gasp should be 15 """
        keys = self.font.keys()
        self.assertIn('gasp', keys, msg="GASP table not found")
        self.assertEqual(type({}), type(self.font['gasp'].gaspRange),
            msg="GASP table: gaspRange method value have wrong type")
        self.assertTrue(self.font['gasp'].gaspRange.has_key(65535))
        # XXX: Needs review
        self.assertEqual(self.font['gasp'].gaspRange[65535], 15)

