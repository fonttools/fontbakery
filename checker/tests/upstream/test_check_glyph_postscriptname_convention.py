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
import re

from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckPostscriptnameGlyphConventions(TestCase):

    path = '.'
    name = __name__
    targets = ['upstream-ttx']
    tool = 'lint'

    def test_Check_Postscriptname_Glyph_Conventions(self):
        """ Check glyphs names comply with PostScript conventions """
        font = Font.get_ttfont(self.path)
        for glyph in font.glyphs():
            if glyph == '.notdef':
                continue
            if not re.match('(^[.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyph):
                self.fail(('Glyph "%s" does not comply conventions.'
                           ' A glyph name may be up to 31 characters in length,'
                           ' must be entirely comprised of characters from'
                           ' the following set:'
                           ' A-Z a-z 0-9 .(period) _(underscore). and must not'
                           ' start with a digit or period. The only exception'
                           ' is the special character ".notdef". "twocents",'
                           ' "a1", and "_" are valid glyph names. "2cents"'
                           ' and ".twocents" are not.'))
