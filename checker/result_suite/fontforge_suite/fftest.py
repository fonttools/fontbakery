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
import fontforge
import unicodedata


class SimpleTest(TestCase):
    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    # def test_ok(self):
    #     """ This test succeeds """
    #     self.assertTrue(True)
    #
    # def test_failure(self):
    #     """ This test fails """
    #     self.assertTrue(False)
    #
    # def test_error(self):
    #     """ Unexpected error """
    #     1 / 0
    #     self.assertTrue(False)

    def test_is_fsType_not_set(self):
        """Is the OS/2 table fsType set to 0?"""
        self.assertEqual(self.font.os2_fstype, 1)

    def test_nbsp(self):
        """Check if 'NO-BREAK SPACE' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('NO-BREAK SPACE')) in self.font)

    def test_space(self):
        """Check if 'SPACE' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('SPACE')) in self.font)

    @tags('required',)
    def test_nbsp_and_space_glyphs_width(self):
        """ Nbsp and space glyphs should have the same width"""
        space = 0
        nbsp = 0
        for x in self.font.glyphs():
            if x.unicode == 160:
                nbsp = x.width
            elif x.unicode == 32:
                space = x.width
        self.assertEqual(space, nbsp)

    def test_euro(self):
        """Check if 'EURO SIGN' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('EURO SIGN')) in self.font)
