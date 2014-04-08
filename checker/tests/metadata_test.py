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

import html5lib
import json
import os
import re
import requests

from checker.base import BakeryTestCase as TestCase


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRAPE_DATAROOT = os.path.join(ROOT, 'scripts', 'scrapes', 'json')


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
        },
        'fontbureau.com': {
            'url': 'http://www.fontbureau.com/search/?q={}',
            'checkText': '<h5>Font results</h5> <div class="rule"></div> '
                         '<span class="note">(No results)</span>'
        },
        'houseind.com': {
            'url': 'http://www.houseind.com/search/?search=Oswald',
            'checkText': '<ul id="related-fonts"> <li class="first">No results.</li> </ul>'
        }
    }

    def setUp(self):
        self.metadata = json.load(open(self.path))

    def test_does_not_familyName_exist_in_myfonts_catalogue(self):
        """ MYFONTS.com """
        test_catalogue = self.rules['myfonts.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_daltonmaag_catalogue(self):
        """ DALTONMAAG.com """
        test_catalogue = self.rules['daltonmaag.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_fontsmith_catalogue(self):
        """ FONTSMITH.com """
        test_catalogue = self.rules['fontsmith.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_fontbureau_catalogue(self):
        """ FONTBUREAU.com """
        test_catalogue = self.rules['fontbureau.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_houseind_catalogue(self):
        """ HOUSEIND.com """
        test_catalogue = self.rules['houseind.com']
        self.check(test_catalogue)

    def test_does_not_familyName_exist_in_terminaldesign_catalogue(self):
        """ TERMINALDESIGN.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'terminaldesign.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_typography_catalogue(self):
        """ TYPOGRAPHY.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'typography.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_europatype_catalogue(self):
        """ EUROPATYPE.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'europatype.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_boldmonday_catalogue(self):
        """ BOLDMONDAY.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'boldmonday.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_commercialtype_catalogue(self):
        """ COMMERCIALTYPE.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'commercialtype.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_swisstypefaces_catalogue(self):
        """ SWISSTYPEFACES.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'swisstypefaces.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_grillitype_catalogue(self):
        """ GRILLITYPE.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'grillitype.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_letterror_catalogue(self):
        """ LETTERROR.com """
        try:
            datafile = open(os.path.join(SCRAPE_DATAROOT, 'letterror.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_veer_catalogue(self):
        """ VEER.com """
        url = 'http://search.veer.com/json/?keyword={}&producttype=TYP&segment=DEF'.format(self.metadata['name'])
        response = requests.get(url)
        if response.status_code == 200:
            self.assertFalse(bool(response.json()['TotalCount']['type']))
        else:
            self.assertTrue(False)

    def test_does_not_familyName_exist_in_fontscom_catalogue(self):
        """ FONTS.com """
        url = 'http://www.fonts.com/browse/font-lists?part={}'.format(self.metadata['name'][0])
        response = requests.get(url)
        if response.status_code == 200:
            tree = html5lib.treebuilders.getTreeBuilder("lxml")
            parser = html5lib.HTMLParser(tree=tree,
                                         namespaceHTMLElements=False)
            doc = parser.parse(response.text)
            f = doc.xpath('//ul/li/a[@class="product productpopper"]/text()')
            self.assertFalse(self.metadata['name'] in map(lambda x: unicode(x).lower(), list(f)))
        else:
            self.assertTrue(False)

    def test_does_not_familyName_exist_in_fontshop_catalogue(self):
        """ FONTSHOP.com """
        url = 'http://www.fontshop.com/service/familiesService.php?dataType=json&searchltr={}'.format(self.metadata['name'][0])
        response = requests.get(url)
        if response.status_code == 200:
            jsondata = response.json()
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['name'].lower(), jsondata))
        else:
            self.assertTrue(False)

    def check(self, test_catalogue):
        url = test_catalogue['url'].format(self.metadata['name'])

        if test_catalogue.get('method') == 'post':
            data = {test_catalogue['keywordParam']: self.metadata['name']}
            response = requests.post(url, allow_redirects=False,
                                     data=data)
        else:
            response = requests.get(url, allow_redirects=False)
        if response.status_code == 200:
            regex = re.compile('\s+')
            self.assertTrue(test_catalogue['checkText'] in regex.sub(' ', response.text))
        elif response.status_code == 302:  # 302 Moved Temporarily
            self.assertTrue(True)
        else:
            self.assertTrue(False)
