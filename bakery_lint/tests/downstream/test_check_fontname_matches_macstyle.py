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
from bakery_lint.base import BakeryTestCase as TestCase
from bakery_cli.ttfont import Font


class CheckFontNameEqualToMacStyleFlags(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_fontname_is_equal_to_macstyle(self):
        """ Check that fontname is equal to macstyle flags """
        font = Font.get_ttfont(self.operator.path)

        macStyle = font.macStyle

        try:
            fontname_style = font.fullname.split('-')[1]
        except IndexError:
            fontname_style = ''

        expected_style = ''
        if macStyle & 0b01:
            expected_style += 'Bold'

        if macStyle & 0b10:
            expected_style += 'Italic'

        if not bool(macStyle & 0b11):
            expected_style = 'Regular'

        if fontname_style != expected_style:
            _ = 'macStyle ({0}) supposed style ended with "{1}"'

            if fontname_style:
                _ += ' but ends with "{2}"'
            self.fail(_.format(bin(macStyle)[-2:], expected_style, fontname_style))
