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
from checker.ttfont import FontTool


REQUIRED_TABLES = set(['cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name',
                       'OS/2', 'post', 'glyf'])
OPTIONAL_TABLES = set(['cvt', 'fpgm', 'loca', 'prep', 'CFF',
                       'VORG', 'EBDT', 'EBLC', 'EBSC', 'BASE', 'GPOS',
                       'GSUB', 'JSTF', 'DSIG', 'gasp', 'hdmx', 'kern',
                       'LTSH', 'PCLT', 'VDMX', 'vhea', 'vmtx'])


class CheckNoProblematicFormats(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_check_no_problematic_formats(self):
        tables = set(FontTool.get_tables(self.path))
        desc = []
        if REQUIRED_TABLES ^ tables:
            desc += ["Font is missing required tables: [%s]" % (REQUIRED_TABLES ^ tables)]
            if OPTIONAL_TABLES & tables:
                desc += ["includes optional tables %s" % (OPTIONAL_TABLES & tables)]
        if desc:
            self.fail(' but '.join(desc))

