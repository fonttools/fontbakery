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


class FontForgeValidateStateTest(TestCase):

    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'
    longMessage = True

    def setUp(self):
        font = fontforge.open(self.path)
        self.validation_state = font.validate()

    def test_validation_open_contours(self):
        """ Glyphs do not have opened contours """
        self.assertFalse(bool(self.validation_state & 0x2))

    def test_validation_glyph_intersect(self):
        """ Glyphs do not intersect somewhere """
        self.assertFalse(bool(self.validation_state & 0x4))

    def test_wrong_direction_in_glyphs(self):
        """ Contours do not have wrong direction """
        self.assertFalse(bool(self.validation_state & 0x8))

    def test_flipped_reference_in_glyphs(self):
        """ Reference in the glyph haven't been flipped """
        self.assertFalse(bool(self.validation_state & 0x10))

    def test_missing_extrema_in_glyphs(self):
        """ Glyphs do not have missing extrema """
        self.assertFalse(bool(self.validation_state & 0x20))

    def test_referenced_glyphs_are_present(self):
        """ Glyph names referred to from glyphs present in the font """
        self.assertFalse(bool(self.validation_state & 0x40))

    def test_points_are_not_too_far_apart(self):
        """ Points (or control points) are not too far apart """
        self.assertFalse(bool(self.validation_state & 0x40000))

    def test_postscript_hasnt_limit_points_in_glyphs(self):
        """ PostScript has not a limit of 1500 points in glyphs """
        self.assertFalse(bool(self.validation_state & 0x80))

    def test_postscript_hasnt_limit_hints_in_glyphs(self):
        """ PostScript hasnt a limit of 96 hints in glyphs """
        self.assertFalse(bool(self.validation_state & 0x100))

    def test_valid_glyph_names(self):
        """ Font doesn't have invalid glyph names """
        self.assertFalse(bool(self.validation_state & 0x200))

    def test_allowed_numbers_points_in_glyphs(self):
        """ Glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x400))

    def test_allowed_numbers_paths_in_glyphs(self):
        """ Glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x800))

    def test_allowed_numbers_points_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x1000))

    def test_allowed_numbers_paths_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x2000))

    def test_valid_length_instructions(self):
        """ Glyphs instructions have valid lengths """
        self.assertFalse(bool(self.validation_state & 0x4000))

    def test_points_are_integer_aligned(self):
        """ Points in glyphs are integer aligned """
        self.assertFalse(bool(self.validation_state & 0x80000))

    def test_missing_anchors(self):
        """ Glyphs have not missing anchor.

            According to the opentype spec, if a glyph contains an anchor point
            for one anchor class in a subtable, it must contain anchor points
            for all anchor classes in the subtable. Even it, logically,
            they do not apply and are unnecessary. """
        self.assertFalse(bool(self.validation_state & 0x100000))

    def test_duplicate_glyphs(self):
        """ Font does not have duplicated glyphs.

            Two (or more) glyphs in this font have the same name. """
        self.assertFalse(bool(self.validation_state & 0x200000))

    def test_duplicate_unicode_codepoints(self):
        """ Glyphs do not have duplicate unicode code points.

            Two (or more) glyphs in this font have the code point. """
        self.assertFalse(bool(self.validation_state & 0x400000))

    def test_overlapped_hints(self):
        """ Glyphs do not have overlapped hints """
        self.assertFalse(bool(self.validation_state & 0x800000))
