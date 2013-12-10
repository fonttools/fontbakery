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
from fontTools.ttLib import TTFont

class SimpleTTXTest(TestCase):
    targets = ['ttx']
    tool   = 'fontTools'
    name   = __name__
    path   = '.'

    def setUp(self):
        # TODO: Need somebody to check this options
        font = TTFont(None, lazy=False, recalcBBoxes=True,
            verbose=False, allowVID=False)
        font.importXML(self.path, quiet=True)
        self.font = font
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    # def test_ok(self):
    #     """ This test succeeds """
    #     self.assertTrue(True)
    #
    # def test_failure(self):
    #     """ This test fails """
    #     self.assertTrue(False)
    #
    # def test_error(self):
    #     """ Unexpected error """
    #     1 / 0
    #     self.assertTrue(False)

    def test_os2_in_keys(self):
        """ This very important test checking if OS/2 is in keys method """
        self.assertIn('OS/2', self.font.keys())

