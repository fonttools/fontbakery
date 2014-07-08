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
from checker.base import BakeryTestCase as TestCase
from checker.ttfont import Font


class CheckFullFontNameBeginsWithFamilyName(TestCase):

    path = '.'
    targets = ['result']
    tool = 'lint'
    name = __name__

    def test_check_full_font_name_begins_with_family_name(self):
        """ Check if full font name begins with the font family name """
        font = Font.get_ttfont(self.path)
        for entry in font.names:
            if entry.nameID != 1:
                continue
            for entry2 in font.names:
                if entry2.nameID != 4:
                    continue
                if (entry.platformID == entry2.platformID
                        and entry.platEncID == entry2.platEncID
                        and entry.langID == entry2.langID):

                    entry2value = Font.bin2unistring(entry2)
                    entryvalue = Font.bin2unistring(entry)
                    if not entry2value.startswith(entryvalue):
                        _ = ('Full font name does not begin with family'
                             ' name: FontFamilyName = "%s";'
                             ' FullFontName = "%s"')
                        self.fail(_ % (entryvalue, entry2value))
