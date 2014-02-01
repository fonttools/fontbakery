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

class SimpleTest(TestCase):
    targets = ['upstream']
    tool   = 'FontForge'
    name   = __name__
    path   = '.'

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

import robofab.world
import robofab.objects


class UfoOpenTest(TestCase):
    targets = ['upstream']
    tool = 'Robofab'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = robofab.world.OpenFont(self.path)
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    # def test_success(self):
    #     """ This test succeeded """
    #     self.assertTrue(True)
    #
    # def test_failure(self):
    #     """ This test failed """
    #     self.assertTrue(False)
    #
    # def test_error(self):
    #     """ Unexpected error """
    #     1 / 0
    #     self.assertTrue(False)

    def test_it_exists(self):
        """ Does this UFO path exist? """
        self.assertEqual(os.path.exists(self.path), True)

    def test_is_folder(self):
        """ Is this UFO really a folder?"""
        self.assertEqual(os.path.isdir(self.path), True)

    def test_is_ended_ufo(self):
        """ Does this font file's name end with '.ufo'?"""
        self.assertEqual(self.path.lower().endswith('.ufo'), True)

    def test_is_A(self):
        """ Does this font have a glyph named 'A'?"""
        self.assertTrue(self.font.has_key('A'))

    def test_is_A_a_glyph_instance(self):
        """ Is this font's property A an instance of an RGlyph object? """
        if self.font.has_key('A'):
            a = self.font['A']
        else:
            a = None
        self.assertIsInstance(a, robofab.objects.objectsRF.RGlyph)

    def test_is_fsType_eq_1(self):
        """Is the OS/2 table fsType set to 0?"""
        desiredFsType = [0]
        self.assertEqual(self.font.info.openTypeOS2Type, desiredFsType)

    # TODO check if this is a good form of test
    def has_character(self, unicodeString):
        """Does this font include a glyph for the given unicode character?"""
        # TODO check the glyph has at least 1 contour
        character = unicodeString[0]
        glyph = None
        if self.font.has_key(character):
            glyph = self.font[character]
        self.assertIsInstance(glyph, robofab.objects.objectsRF.RGlyph)

    def test_has_rupee(self):
        u"""Does this font include a glyph for ₹, the Indian Rupee Sign codepoint?"""
        has_character(self, u'₹')

    def areAllFamilyNamesTheSame(paths):
        """
        Test if all family names in the UFOs given to this method as paths are the same.
        There is probably a MUCH more elegant way to do this :)
        TODO: Make this test for families where the familyName differs but there are OT names that compensate (common with fonts made with compatibility with Windows GDI applications in mind)
        """
        fonts = []
        allFamilyNamesAreTheSame = False
        for path in paths:
            font = OpenFont(path)
            print font
            fonts.append(font)
        regularFamilyName = "unknown"
        for path in paths:
            if path.endswith('Regular.ufo'):
                regularFamilyName = font.info.familyName
        print 'regularFamilyName is', regularFamilyName
        for font in fonts:
            if font.info.familyName == regularFamilyName: # TODO or font.info.openTypeNamePreferredFamilyName == regularFamilyName:
                allFamilyNamesAreTheSame = True
        if allFamilyNamesAreTheSame == True:
            return True
        else:
            return False

    def ifAllFamilyNamesAreTheSame(paths): # TODO should be test_ifallFamilyNamesAreTheSame
        allFamilyNamesAreTheSame = areAllFamilyNamesTheSame(paths)
        assert allFamilyNamesAreTheSame
    # TODO: check the stems of the style name and full names match the
    # familyNames
