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


class CheckFontHasDsigTable(TestCase):

    name = __name__
    targets = ['result']
    tool = 'lint'

    @autofix('bakery_cli.fixers.CreateDSIGFixer')
    def test_check_font_has_dsig_table(self):
        """ Check that font has DSIG table """
        font = Font.get_ttfont(self.operator.path)
        try:
            font['DSIG']
        except KeyError:
            self.fail('Font does not have "DSIG" table')


class CheckFontHasNotKernTable(TestCase):

    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_no_kern_table_exists(self):
        """ Check that no "KERN" table exists """
        font = Font.get_ttfont(self.operator.path)
        try:
            font['KERN']
            self.fail('Font does have "KERN" table')
        except KeyError:
            pass
