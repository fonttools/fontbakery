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
import magic
import os

from checker.base import BakeryTestCase as TestCase, tags
from cli.ttfont import Font


class CheckFontAgreements(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def setUp(self):
        self.font = Font.get_ttfont(self.path)

    @tags('required')
    def test_em_is_1000(self):
        """ Font em should be equal 1000 """
        self.assertEqual(self.font.get_upm_height(), 1000)

    @tags('required')
    def test_is_fsType_not_set(self):
        """Is the OS/2 table fsType set to 0?"""
        self.assertEqual(self.font.OS2_fsType, 0)

    @tags('required')
    def test_latin_file_exists(self):
        """ Check latin subset font file exists """
        path = os.path.dirname(self.path)
        path = os.path.join(path, self.path[:-3] + "latin")
        self.assertTrue(os.path.exists(path))

    @tags('required')
    def test_file_is_font(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(magic.from_file(self.path), 'TrueType font data')

    @tags('required')
    def test_font_is_font(self):
        """ File provided as parameter is TTF font file """
        self.assertTrue(magic.from_file(self.path, mime=True),
                        'application/x-font-ttf')
