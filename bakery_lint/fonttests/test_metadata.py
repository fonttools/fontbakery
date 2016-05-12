""" Contains TestCases for METADATA.pb """
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

    def test_the_same_number_of_glyphs_across_family(self):
        """ The same number of glyphs across family? """
        glyphs_count = 0
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if not glyphs_count:
                glyphs_count = len(ttfont.glyphs)

            if glyphs_count != len(ttfont.glyphs):
                self.fail('Family has a different glyphs\'s count in fonts')

    def test_the_same_names_of_glyphs_across_family(self):
        """ The same names of glyphs across family? """
        glyphs = None
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if not glyphs:
                glyphs = len(ttfont.glyphs)

            if glyphs != len(ttfont.glyphs):
                self.fail('Family has a different glyphs\'s names in fonts')

    def test_the_same_encodings_of_glyphs_across_family(self):
        """ The same unicode encodings of glyphs across family? """
        encoding = None
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            cmap = ttfont.retrieve_cmap_format_4()

            if not encoding:
                encoding = cmap.platEncID

            if encoding != cmap.platEncID:
                self.fail('Family has different encoding across fonts')


