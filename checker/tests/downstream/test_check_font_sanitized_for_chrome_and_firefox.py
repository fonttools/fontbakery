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
from cli.system import prun
from flask import current_app


class OTSTest(TestCase):

    targets = ['result']
    tool = 'OTS'
    name = __name__
    path = '.'

    @tags('required',)
    def test_ots(self):
        """ Is TTF file correctly sanitized for Firefox and Chrome """
        stdout = prun('{0} {1}'.format(current_app.config['OTS_BINARY_PATH'],
                                       self.path),
                      current_app.config['ROOT'])
        self.assertEqual('', stdout.replace('\n', '. '))
