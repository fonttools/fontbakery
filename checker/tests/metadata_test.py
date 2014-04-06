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

import json
import requests

from checker.base import BakeryTestCase as TestCase


class MetadataTest(TestCase):

    targets = ['metadata']
    tool = 'METADATA.json'
    path = '.'
    name = __name__

    def setUp(self):
        self.metadata = json.load(open(self.path))

    def test_is_familyName_existed_in_myfonts_catalogue(self):
        """ Does this font exist in myfonts catalogue? """
        url = 'http://www.myfonts.com/search/name:{}/fonts/'.format(self.metadata['name'])
        response = requests.post(url, allow_redirects=False)
        if response.status_code == 200:
            self.assertTrue('got nothing' in response.text)
        elif response.status_code == 302:  # 302 Moved Temporarily
            self.assertTrue(True)
        else:
            self.assertTrue(False)
