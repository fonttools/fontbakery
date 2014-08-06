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
from cli.ttfont import Font


class CheckItalicAngleAgreement(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    @tags('required')
    def test_check_italic_angle_agreement(self):
        """ Check italicangle property zero or negative """
        font = Font.get_ttfont(self.path)
        if font.italicAngle > 0:
            self.fail('italicAngle must be less or equal zero')
        if abs(font.italicAngle) > 20:
            self.fail('italicAngle can\'t be larger than 20 degrees')
