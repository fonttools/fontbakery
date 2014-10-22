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
import os.path as op

from bakery_lint.base import BakeryTestCase as TestCase, tags


class CheckTextFilesExist(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def assertExists(self, filename):
        if not isinstance(filename, list):
            filename = [filename]

        exist = False
        for p in filename:
            if op.exists(op.join(op.dirname(self.operator.path), p)):
                exist = True
        if not exist:
            self.fail('%s does not exist in project' % filename)

    @tags('required')
    def test_copyrighttxt_exists(self):
        """ Font folder should contains COPYRIGHT.txt """
        self.assertExists('COPYRIGHT.txt')

    @tags('required')
    def test_description_exists(self):
        """ Font folder should contains DESCRIPTION.en_us.html """
        self.assertExists('DESCRIPTION.en_us.html')

    @tags('required')
    def test_licensetxt_exists(self):
        """ Font folder should contains LICENSE.txt """
        self.assertExists(['LICENSE.txt', 'OFL.txt'])

    def test_fontlogtxt_exists(self):
        """ Font folder should contains FONTLOG.txt """
        self.assertExists('FONTLOG.txt')
