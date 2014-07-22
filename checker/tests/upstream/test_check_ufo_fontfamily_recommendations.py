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
import fontforge

from checker.base import BakeryTestCase as TestCase


class UFO_FontFamilyNamingTest(TestCase):

    targets = ['upstream']
    tool = 'FontForge'
    name = __name__
    path = '.'

    def test_ufo_family_naming_recommendation(self):
        """ The font corresponds the font family naming recommendation.
        See http://forum.fontlab.com/index.php?topic=313.0 """
        if (not self.path.lower().endswith('.ufo')
                or not self.path.lower().endswith('.sfd')):
            # This test checks only UFO source font.
            return
        font = fontforge.open(self.path)
        # <Full name> limitation is < 64 chars
        length = len(font.sfnt_names[4][2])
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        # <Postscript name> limitation is < 30 chars
        length = len(font.sfnt_names[6][2])
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        # <Postscript name> may contain only a-zA-Z0-9
        # and one hyphen
        self.assertRegexpMatches(font.sfnt_names[6][2], r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(font.sfnt_names[6][2].count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        # <Family Name> limitation is 32 chars
        length = len(font.sfnt_names[1][2])
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Style Name> limitation is 32 chars
        length = len(font.sfnt_names[2][2])
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Weight> value >= 250 and <= 900 in steps of 50
        self.assertTrue(bool(font.os2_weight % 50 == 0),
                        msg=('Weight has to be in steps of 50.'
                             ' Now: %s') % font.os2_weight)

        self.assertGreaterEqual(font.os2_weight, 250)
        self.assertLessEqual(font.os2_weight, 900)
