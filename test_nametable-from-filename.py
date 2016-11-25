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
import ntpath
from fontTools.ttLib import TTFont
script = __import__("fontbakery-nametable-from-filename")


class FileNameFromTTFName(unittest.TestCase):
    def _font_renaming(self, fonts):
        """Test the filename produces exactly the same name table as the
        font's nametable. Only test against name fields which exist in
        the font."""
        for font in self.fonts:
            font_filename = ntpath.basename(font)
            font_vendor = self.fonts[font]['OS/2'].achVendID
            font_version = str(self.fonts[font]['name'].getName(5, 1, 0, 0))
            new_names = script.NameTableFromFilename(font_filename,
                                                     font_version,
                                                     font_vendor)
            # print new_names.version

            for name_field in new_names:
                font_field = self.fonts[font]['name'].getName(*name_field)
                new_name_field = new_names[name_field]
                if font_field:  # Check the field is in the font
                    enc = font_field.getEncoding()
                    self.assertEqual(str(font_field).decode(enc),
                                     new_name_field,
                                     'ERROR %s: %s != %s' % (font,
                                                             str(font_field),
                                                             new_name_field))
                    print '%s == %s' % (str(font_field).decode(enc),
                                        new_name_field)

    def test_nunito_renaming(self):
        """Nunito Chosen because it has another family Nunito Heavy and a lot
        of weights"""
        f_path = os.path.join('data', 'test', 'nunito')
        self.fonts = {f: TTFont(os.path.join(f_path, f)) for f
                      in os.listdir(f_path) if 'ttf' in f}
        self._font_renaming(self.fonts)

    def test_cabin_renaming(self):
        """Cabin chosen because it has a seperate Condensed family"""
        f_path = os.path.join('data', 'test', 'cabin')
        self.fonts = {f: TTFont(os.path.join(f_path, f)) for f
                      in os.listdir(f_path) if 'ttf' in f}
        self._font_renaming(self.fonts)

    def test_glyphsapp_family_sans_export(self):
        """The ultimate test. Can this naming tool repoduce Google Font's
        Naming schema.
        Source repo here: https://github.com/davelab6/glyphs-export"""
        f_path = os.path.join('data', 'test', 'familysans')
        self.fonts = {f: TTFont(os.path.join(f_path, f)) for f
                      in os.listdir(f_path) if 'ttf' in f}
        self._font_renaming(self.fonts)


if __name__ == '__main__':
    unittest.main()
