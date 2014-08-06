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


class CheckFontNameEqualToMacStyleFlags(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_fontname_is_equal_to_macstyle(self):
        """ Check that fontname is equal to macstyle flags """
        font = Font.get_ttfont(self.path)

        fontname = font.fullname
        macStyle = font.macStyle

        try:
            fontname_style = fontname.split('-')[1]
        except IndexError:
            self.fail(('Fontname is not canonical. Expected it contains '
                       'style. eg.: Italic, BoldItalic, Regular'))

        style = ''
        if macStyle & 0b01:
            style += 'Bold'

        if macStyle & 0b10:
            style += 'Italic'

        if not bool(macStyle & 0b11):
            style = 'Regular'

        if not fontname_style.endswith(style):
            _ = 'macStyle (%s) supposed style ended with "%s" but ends with "%s"'
            self.fail(_ % (bin(macStyle)[-2:], style, fontname_style))
