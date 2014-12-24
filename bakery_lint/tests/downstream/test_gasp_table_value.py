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
from bakery_lint.base import BakeryTestCase as TestCase, autofix
from bakery_cli.ttfont import Font


class CheckGaspTableType(TestCase):

    name = __name__
    targets = ['result']
    tool = 'lint'

    @autofix('bakery_cli.fixers.GaspFixer', always_run=True)
    def test_check_gasp_table_type(self):
        """ Font table gasp should be 15 """
        font = Font.get_ttfont(self.operator.path)
        try:
            font['gasp']
        except KeyError:
            self.fail('"GASP" table not found')

        if not isinstance(font['gasp'].gaspRange, dict):
            self.fail('GASP.gaspRange method value have wrong type')

        if 65535 not in font['gasp'].gaspRange:
            self.fail("GASP does not have 65535 gaspRange")

        # XXX: Needs review
        if font['gasp'].gaspRange[65535] != 15:
            self.fail('gaspRange[65535] value is not 15')
