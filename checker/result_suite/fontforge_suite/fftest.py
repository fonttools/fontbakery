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
import fontforge

class SimpleTest(TestCase):
    target = 'result'
    tool   = 'FontForge'
    name   = __name__
    path   = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)

    def test_is_fsType_not_set(self):
        """Is the OS/2 table fsType set?"""
        self.assertEqual(self.font.os2_fstype, 0)
