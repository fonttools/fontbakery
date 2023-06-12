#!/usr/bin/env python
# Copyright 2013,2016 The Font Bakery Authors.
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
import unittest
import os
from fontTools.ttLib import TTFont

script = __import__("fontbakery-nametable-from-filename")


class NameTableFromTTFName(unittest.TestCase):
    def _font_renaming(self, f_path):
        """The test fonts have been generated from Glyphsapp and conform
        to the googlefonts nametable spec. The test should pass if the new
        nametable matches the test font's name table."""
        fonts_paths = [
            os.path.join(f_path, f) for f in os.listdir(f_path) if ".ttf" in f
        ]

        for font_path in fonts_paths:
            font = TTFont(font_path)
            old_nametable = font["name"]
            new_nametable = script.nametable_from_filename(font_path)

            for field in script.REQUIRED_FIELDS:
                if old_nametable.getName(*field):
                    enc = old_nametable.getName(*field).getEncoding()
                    self.assertEqual(
                        str(old_nametable.getName(*field)).decode(enc),
                        str(new_nametable.getName(*field)).decode(enc),
                    )

    def test_nunito_renaming(self):
        """Nunito Chosen because it has another family Nunito Heavy and a lot
        of weights"""
        f_path = os.path.join("data", "test", "nunito")
        self._font_renaming(f_path)

    def test_cabin_renaming(self):
        """Cabin chosen because it has a seperate Condensed family"""
        f_path = os.path.join("data", "test", "cabin")
        self._font_renaming(f_path)

    def test_glyphsapp_family_sans_export(self):
        """The ultimate test. Can this naming tool repoduce Google Font's
        Naming schema.
        Source repo here: https://github.com/davelab6/glyphs-export"""
        f_path = os.path.join("data", "test", "familysans")
        self._font_renaming(f_path)


if __name__ == "__main__":
    unittest.main()
