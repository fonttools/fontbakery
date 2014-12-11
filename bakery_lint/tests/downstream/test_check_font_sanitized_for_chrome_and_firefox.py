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
import os

from bakery_lint.base import BakeryTestCase as TestCase, tags
from bakery_cli.utils import run


class OTSTest(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    @tags('required',)
    def test_ots(self):
        """ Is TTF file correctly sanitized for Firefox and Chrome """
        stdout = run('{0} {1}'.format('ot-sanitise', self.operator.path),
                      os.path.dirname(self.operator.path),
                      log=self.operator.logger)
        self.assertEqual('', stdout.strip())
