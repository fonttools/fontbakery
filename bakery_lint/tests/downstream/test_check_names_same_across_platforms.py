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
from bakery_cli.ttfont import Font


class CheckNamesSameAcrossPlatforms(TestCase):

    name = __name__
    tool = 'lint'
    targets = ['result']

    @tags('required')
    def test_check_names_same_across_platforms(self):
        """ Font names are same across specific-platforms """
        font = Font.get_ttfont(self.operator.path)

        for name in font.names:
            for name2 in font.names:
                if name.nameID != name2.nameID:
                    continue

                if self.diff_platform(name, name2) or self.diff_platform(name2, name):
                    _name = Font.bin2unistring(name)
                    _name2 = Font.bin2unistring(name2)
                    if _name != _name2:
                        msg = ('Names in "name" table are not the same'
                               ' across specific-platforms')
                        self.fail(msg)

    def diff_platform(self, name, name2):
        return (name.platformID == 3 and name.langID == 0x409
                and name2.platformID == 1 and name2.langID == 0)
