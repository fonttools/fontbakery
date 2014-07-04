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
import types
import unittest

from checker.metadata import Metadata, FamilyMetadata, FontMetadata


class MetadataTestCase(unittest.TestCase):

    def test_family_metadata_is_loaded(self):
        """ Check if Metadata can read family metadata correctly """
        fm = Metadata.get_family_metadata('{"name": "Family Name"}')
        self.assertEqual(type(fm), FamilyMetadata)
        self.assertEqual(fm.name, "Family Name")
        self.assertEqual(fm.designer, "")
        self.assertEqual(fm.license, "")
        self.assertEqual(fm.visibility, "Sandbox")
        self.assertEqual(fm.category, "")
        self.assertEqual(fm.size, 0)
        self.assertEqual(fm.date_added, "")
        self.assertEqual(fm.subsets, [])

    def test_font_metadata_is_loaded(self):
        """ Check if font metadata can be read from family metadata """
        fm = Metadata.get_family_metadata(
            '{"name": "Family Name", "fonts": [{"name": "FontName"}]}')
        fonts_metadata = fm.fonts
        self.assertEqual(type(fonts_metadata), types.GeneratorType)
        fm = fonts_metadata.next()
        self.assertEqual(type(fm), FontMetadata)
        self.assertEqual(fm.name, "FontName")
        self.assertEqual(fm.post_script_name, "")
        self.assertEqual(fm.full_name, "")
        self.assertEqual(fm.style, "normal")
        self.assertEqual(fm.weight, 400)
        self.assertEqual(fm.filename, "")
        self.assertEqual(fm.copyright, "")
