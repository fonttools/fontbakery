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

# HOW TO
# 1. Copy to the $target_suit/$tool_suite/ dir
# 2. Fill in the lines marked with XXX

from checker.base import BakeryTestCase as TestCase
import fontforge # import your testing package

class SampleTest(TestCase):
    targets = ['upstream', 'result']    # XXX pick one or both
    tool   = 'FontForge'                # XXX name the tool
    name   = __name__                   # XXX leave this
    path   = '.'                        # XXX leave this

    def setUp(self):
        self.font = fontforge.open(self.path) # XXX how to open fonts with your testing package
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
