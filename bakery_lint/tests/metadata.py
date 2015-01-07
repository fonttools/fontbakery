""" Contains TestCase for METADATA.json  """
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
from unittest import skip
import json
import magic
import os
import os.path as op
import re
import requests

from bakery_lint.base import BakeryTestCase as TestCase, tags

ROOT = op.abspath(op.join(op.dirname(__file__), '..', '..'))
SCRAPE_DATAROOT = op.join(ROOT, 'bakery_cli', 'scrapes', 'json')


def get_test_subset_function(path):
    def function(self):

        if not op.exists(path):
            self.fail('%s subset does not exist' % op.basename(path))

        if magic.from_file(path) != 'TrueType font data':
            _ = '%s does not seem to be truetype font'
            self.fail(_ % op.basename(path))
    function.tags = ['required']
    return function


class MetadataSubsetsListTest(TestCase):

    targets = ['metadata']
    tool = 'METADATA.json'
    name = __name__

    @classmethod
    def __generateTests__(cls):
        metadata = json.load(open(cls.operator.path))
        for font in metadata.get('fonts', []):
            for subset in metadata.get('subsets', []) + ['menu']:
                path = op.join(op.dirname(cls.operator.path),
                               font.get('filename')[:-3] + subset)

                subsetid = re.sub(r'\W', '_', subset)

                # cls.operator.debug('cls.test_charset_{0} = get_test_subset_function("{1}")'.format(subsetid, path))
                # cls.operator.debug('cls.test_charset_{0}.__func__.__doc__ = "{1} is real TrueType file"'.format(subsetid, font.get('filename')[:-3] + subset))

                exec 'cls.test_charset_{0} = get_test_subset_function("{1}")'.format(subsetid, path)
                exec 'cls.test_charset_{0}.__func__.__doc__ = "{1} is real TrueType file"'.format(subsetid, font.get('filename')[:-3] + subset)



class MetadataTest(TestCase):

    targets = ['metadata']
    tool = 'METADATA.json'
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
        self.metadata = json.load(open(self.operator.path))

    def test_description_is_valid_html(self):
        """ DESCRIPTION.en_us.html is not real html file """
        p = op.join(op.dirname(self.operator.path), 'DESCRIPTION.en_us.html')
        msg = 'DESCRIPTION.en_us.html is not real html file'
        self.assertEqual(magic.from_file(p, mime=True), 'text/html', msg)

    def test_description_is_more_than_500b(self):
        """ DESCRIPTION.en_us.html is more than 500 bytes """
        p = op.join(op.dirname(self.operator.path), 'DESCRIPTION.en_us.html')
        msg = 'DESCRIPTION.en_us.html is not real html file'
        statinfo = os.stat(p)
        msg = 'DESCRIPTION.en_us.html must have size larger than 500 bytes'
        self.assertGreater(statinfo.st_size, 500, msg)

    def test_family_is_listed_in_gwf(self):
        """ Fontfamily is listed in Google Font Directory """
        url = 'http://fonts.googleapis.com/css?family=%s' % self.metadata['name'].replace(' ', '+')
        fp = requests.get(url)
        self.assertTrue(fp.status_code == 200, 'No family found in GWF in %s' % url)
        self.assertEqual(self.metadata.get('visibility'), 'External')

    @tags('required')
    def test_metadata_designer_exists_in_profiles_csv(self):
        """ Designer exists in GWF profiles.csv """
        designer = self.metadata.get('designer', u'')
        self.assertTrue(designer, 'Field "designer" MUST NOT be empty')
        import urllib
        import csv
        fp = urllib.urlopen('https://googlefontdirectory.googlecode.com/hg/designers/profiles.csv')
        designers = []
        for row in csv.reader(fp):
            if not row:
                continue
            designers.append(row[0].decode('utf-8'))
        self.assertTrue(designer in designers,
                        msg='Designer %s is not in profiles.csv' % designer)

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

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'terminaldesign.json')))
    def test_does_not_familyName_exist_in_terminaldesign_catalogue(self):
        """ TERMINALDESIGN.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'terminaldesign.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'typography.json')))
    def test_does_not_familyName_exist_in_typography_catalogue(self):
        """ TYPOGRAPHY.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'typography.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'europatype.json')))
    def test_does_not_familyName_exist_in_europatype_catalogue(self):
        """ EUROPATYPE.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'europatype.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'boldmonday.json')))
    def test_does_not_familyName_exist_in_boldmonday_catalogue(self):
        """ BOLDMONDAY.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'boldmonday.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'commercialtype.json')))
    def test_does_not_familyName_exist_in_commercialtype_catalogue(self):
        """ COMMERCIALTYPE.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'commercialtype.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'swisstypefaces.json')))
    def test_does_not_familyName_exist_in_swisstypefaces_catalogue(self):
        """ SWISSTYPEFACES.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'swisstypefaces.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'grillitype.json')))
    def test_does_not_familyName_exist_in_grillitype_catalogue(self):
        """ GRILLITYPE.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'grillitype.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'letterror.json')))
    def test_does_not_familyName_exist_in_letterror_catalogue(self):
        """ LETTERROR.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'letterror.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'teff.json')))
    def test_does_not_familyName_exist_in_teff_catalogue(self):
        """ TEFF.nl """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'teff.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'nouvellenoire.json')))
    def test_does_not_familyName_exist_in_nouvellenoire_catalogue(self):
        """ NOUVELLENOIRE.ch """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'nouvellenoire.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'typedifferent.json')))
    def test_does_not_familyName_exist_in_typedifferent_catalogue(self):
        """ TYPEDIFFERENT.com """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'typedifferent.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    @skip(not op.exists(op.join(SCRAPE_DATAROOT, 'optimo.json')))
    def test_does_not_familyName_exist_in_optimo_catalogue(self):
        """ OPTIMO.ch """
        try:
            datafile = open(op.join(SCRAPE_DATAROOT, 'optimo.json'))
            catalogue = json.load(datafile)
            self.assertFalse(self.metadata['name'].lower() in map(lambda x: x['title'].lower(), catalogue))
        except (OSError, IOError):
            assert False, 'Run `make crawl` to get latest data'

    def test_does_not_familyName_exist_in_veer_catalogue(self):
        """ VEER.com """
        url = 'http://search.veer.com/json/?keyword={}&producttype=TYP&segment=DEF'.format(self.metadata['name'])
        try:
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                self.assertFalse(bool(response.json()['TotalCount']['type']))
            else:
                self.assertTrue(False)
        except requests.exceptions.Timeout:
            self.assertTrue(False)

    def test_does_not_familyName_exist_in_fontscom_catalogue(self):
        """ FONTS.com """
        url = 'http://www.fonts.com/browse/font-lists?part={}'.format(self.metadata['name'][0])
        try:
            response = requests.get(url, timeout=0.2)
        except requests.exceptions.Timeout:
            self.assertTrue(False)
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
        try:
            response = requests.get(url, timeout=0.2)
        except requests.exceptions.Timeout:
            self.assertTrue(False)
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
            try:
                response = requests.get(url, allow_redirects=False, timeout=0.2)
            except requests.exceptions.Timeout:
                self.assertTrue(False)
        if response.status_code == 200:
            regex = re.compile('\s+')
            self.assertTrue(test_catalogue['checkText'] in regex.sub(' ', response.text))
        elif response.status_code == 302:  # 302 Moved Temporarily
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_metadata_fonts_no_dupes(self):
        """ METADATA.json fonts propery only should have uniq values """
        fonts = {}
        for x in self.metadata.get('fonts', None):
            self.assertFalse(x.get('fullName', '') in fonts)
            fonts[x.get('fullName', '')] = x

        self.assertEqual(len(set(fonts.keys())),
                         len(self.metadata.get('fonts', None)))

    @tags('required')
    def test_metadata_keys(self):
        """ METADATA.json should have top keys: ["name", "designer",
            "license", "visibility", "category", "size", "dateAdded",
            "fonts", "subsets"] """

        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]

        for key in top_keys:
            self.assertIn(key, self.metadata, msg="Missing %s key" % key)

    @tags('required')
    def test_metadata_fonts_key_list(self):
        """ METADATA.json font key should be list """
        self.assertEqual(type(self.metadata.get('fonts', '')), type([]))

    @tags('required')
    def test_metadata_subsets_key_list(self):
        """ METADATA.json subsets key should be list """
        self.assertEqual(type(self.metadata.get('subsets', '')), type([]))

    @tags('required')
    def test_metadata_fonts_items_dicts(self):
        """ METADATA.json fonts key items are dicts """
        for x in self.metadata.get('fonts', None):
            self.assertEqual(type(x), type({}), msg="type(%s) is not dict" % x)

    @tags('required')
    def test_metadata_top_keys_types(self):
        """ METADATA.json should have proper top keys types """
        self.assertEqual(type(self.metadata.get("name", None)),
                         type(u""), msg="'name' is {0}, but must be {1}".format(type(self.metadata.get("name", None)), type(u"")))

        self.assertEqual(type(self.metadata.get("designer", None)),
                         type(u""), msg="'designer' is {0}, but must be {1}".format(type(self.metadata.get("designer", None)), type(u"")))

        self.assertEqual(type(self.metadata.get("license", None)),
                         type(u""), msg="'license' is {0}, but must be {1}".format(type(self.metadata.get("license", None)), type(u"")))

        self.assertEqual(type(self.metadata.get("visibility", None)),
                         type(u""), msg="'visibility' is {0}, but must be {1}".format(type(self.metadata.get("visibility", None)), type(u"")))

        self.assertEqual(type(self.metadata.get("category", None)),
                         type(u""), msg="'category' is {0}, but must be {1}".format(type(self.metadata.get("category", None)), type(u"")))

        self.assertEqual(type(self.metadata.get("size", None)),
                         type(0), msg="'size' is {0}, but must be {1}".format(type(self.metadata.get("size", None)), type(u"")))

        self.assertEqual(type(self.metadata.get("dateAdded", None)),
                         type(u""), msg="'dateAdded' is {0}, but must be {1}".format(type(self.metadata.get("dateAdded", None)), type(u"")))

    @tags('required')
    def test_metadata_no_unknown_top_keys(self):
        """ METADATA.json don't have unknown top keys """
        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]
        for x in self.metadata.keys():
            self.assertIn(x, top_keys, msg="%s found unknown top key" % x)

    @tags('required')
    def test_metadata_atleast_latin_menu_subsets_exist(self):
        """ METADATA.json subsets should have at least 'menu' and 'latin' """
        self.assertIn('menu', self.metadata.get('subsets', []),
                      msg="Subsets missing menu")
        self.assertIn('latin', self.metadata.get('subsets', []),
                      msg="Subsets missing latin")

    @tags('required')
    def test_metadata_license(self):
        """ METADATA.json license is 'Apache2', 'UFL' or 'OFL' """
        licenses = ['Apache2', 'OFL', 'UFL']
        self.assertIn(self.metadata.get('license', ''), licenses)

    @tags('required')
    def test_metadata_has_unique_style_weight_pairs(self):
        """ METADATA.json only contains unique style:weight pairs """
        pairs = []
        for fontdata in self.metadata.get('fonts', []):
            styleweight = '%s:%s' % (fontdata['style'],
                                     fontdata.get('weight', 0))
            self.assertNotIn(styleweight, pairs)
            pairs.append(styleweight)
