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

    rules = {
        'myfonts.com': {
            'url': 'http://www.myfonts.com/search/name:{}/fonts/',
            'checkText': 'I&rsquo;ve got nothing'
        },
        'daltonmaag.com': {
            'url': 'http://www.daltonmaag.com/search.html?term={}',
            'checkText': 'No product families matched your search term'
        },
        'fontsmith.com': {
            'url': 'http://www.fontsmith.com/support/search-results.cfm',
            'checkText': "Showing no search results for",
            'method': 'post',
            'keywordParam': 'search'
        }
    }

    def setUp(self):
        self.metadata = json.load(open(self.path))

    def test_does_not_familyName_exist_in_myfonts_catalogue(self):
        """ Does not this font exist in catalogue? MYFONTS.com """
        test_catalogue = self.rules['myfonts.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_daltonmaag_catalogue(self):
        """ Does not this font exist in catalogue? DALTONMAAG.com """
        test_catalogue = self.rules['daltonmaag.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_fontsmith_catalogue(self):
        """ Does not this font exist in catalogue? FONTSMITH.com """
        test_catalogue = self.rules['fontsmith.com']
        self.check(test_catalogue)

    def check(self, test_catalogue):
        url = test_catalogue['url'].format(self.metadata['name'])

        if test_catalogue.get('method') == 'post':
            data = {test_catalogue['keywordParam']: self.metadata['name']}
            response = requests.post(url, allow_redirects=False,
                                     data=data)
        else:
            response = requests.get(url, allow_redirects=False)
        if response.status_code == 200:
            self.assertTrue(test_catalogue['checkText'] in response.text)
        elif response.status_code == 302:  # 302 Moved Temporarily
            self.assertTrue(True)
        else:
            self.assertTrue(False)
