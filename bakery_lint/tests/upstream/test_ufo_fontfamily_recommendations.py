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
from __future__ import print_function
import fontforge

from bakery_lint.base import BakeryTestCase as TestCase


def ufo_required(f):

    def func(self, *args, **kwargs):
        if (not self.operator.path.lower().endswith('.ufo')
                and not self.operator.path.lower().endswith('.sfd')):
            # This test checks only UFO source font.
            return

        return f(self, *args, **kwargs)

    return func


class TestUFOFontFamilyNamingTest(TestCase):
    "The font follows the font family naming recommendation"
    # See http://forum.fontlab.com/index.php?topic=313.0

    targets = ['upstream']
    # TODO use robofab to test this in UFOs
    tool = 'FontForge'
    name = __name__

    @ufo_required
    def test_fullfontname_less_than_64_chars(self):
        """ <Full name> limitation is < 64 chars """
        font = fontforge.open(self.operator.path)
        length = len(font.sfnt_names[4][2])
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

    @ufo_required
    def test_postscriptname_less_than_30_chars(self):
        """ <Postscript name> limitation is < 30 chars """
        font = fontforge.open(self.operator.path)
        length = len(font.sfnt_names[6][2])
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

    @ufo_required
    def test_postscriptname_consistof_allowed_chars(self):
        """ <Postscript name> may contain only a-zA-Z0-9 and one hyphen """
        font = fontforge.open(self.operator.path)
        self.assertRegexpMatches(font.sfnt_names[6][2],
                                 r'^[a-zA-Z0-9]+\-?[a-zA-Z0-9]+$',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))

    @ufo_required
    def test_familyname_less_than_32_chars(self):
        """ <Family Name> limitation is 32 chars """
        font = fontforge.open(self.operator.path)
        length = len(font.sfnt_names[1][2])
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

    @ufo_required
    def test_stylename_less_than_32_chars(self):
        """ <Style Name> limitation is 32 chars """
        font = fontforge.open(self.operator.path)
        length = len(font.sfnt_names[2][2])
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

    @ufo_required
    def test_weight_value_range_between_250_and_900(self):
        """ <Weight> value >= 250 and <= 900 in steps of 50 """
        font = fontforge.open(self.operator.path)
        self.assertTrue(bool(font.os2_weight % 50 == 0),
                        msg=('Weight has to be in steps of 50.'
                             ' Now: %s') % font.os2_weight)

        self.assertGreaterEqual(font.os2_weight, 250)
        self.assertLessEqual(font.os2_weight, 900)
