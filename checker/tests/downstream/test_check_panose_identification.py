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
from cli.ttfont import Font


class CheckPanoseIdentification(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_check_panose_identification(self):
        font = Font.get_ttfont(self.path)

        if font['OS/2'].panose['bProportion'] == 9:
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    link = ('http://www.thomasphinney.com/2013/01'
                            '/obscure-panose-issues-for-font-makers/')
                    self.fail(('Your font does not seem monospaced but PANOSE'
                               ' bProportion set to monospace. It may have '
                               ' a bug in windows. Details: %s' % link))
                prev = font.advance_width(g)
