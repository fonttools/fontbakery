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
from fontaine.font import Font
import re, string

class FontaineTest(TestCase):
    targets = ['result']
    tool   = 'pyfontaine'
    name   = __name__
    path   = '.'

    def setUp(self):
        self.font = Font(self.path)
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
    
    def test_charMaker(self):
        # import ipdb; ipdb.set_trace()
        pattern = re.compile('[\W_]+')
        functionTemplate = """def test_charset_%s(self, p): self.test_charset_%s.__func__.__doc__ = "Is %s covered 100%%?"; self.assertTrue(p == 100)"""
        for orthographyTuple in self.font.get_orthographies():
            charmap = orthographyTuple[0]
            percent = orthographyTuple[2]
            shortname = pattern.sub('', charmap.common_name)
            print "TODO: This doesn't work yet..."
            print functionTemplate % (shortname, shortname, charmap.common_name)
            print 'test_charset_%s(self, 100)' % shortname
            exec functionTemplate % (shortname, shortname, charmap.common_name)
            exec 'test_charset_%s(self, 100)' % shortname
