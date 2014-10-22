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
from bakery_lint.base import BakeryTestCase as TestCase
from bakery_cli.ttfont import Font


class CheckOS2WidthClass(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_check_os2_width_class(self):
        font = Font.get_ttfont(self.operator.path)
        error = "OS/2 widthClass must be [1..9] inclusive, was %s IE9 fail"
        error = error % font.OS2_usWidthClass
        self.assertIn(font.OS2_usWidthClass, range(1, 10), error)
