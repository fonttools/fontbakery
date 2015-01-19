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

from bakery_cli.ttfont import Font
from bakery_lint.base import BakeryTestCase as TestCase, tags
from bakery_lint.metadata import Metadata

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

class TestFontOnDiskFamilyEqualToMetadataJSON(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required',)
    def test_font_on_disk_family_equal_in_metadata_json(self):
        """ Font on disk and in METADATA.json have the same family name """
        contents = self.read_metadata_contents()
        metadata = Metadata.get_family_metadata(contents)

        unmatched_fonts = []
        for font_metadata in metadata.fonts:
            try:
                font = Font.get_ttfont_from_metadata(self.operator.path,
                                                     font_metadata)
            except IOError:
                continue
            if font.familyname != font_metadata.name:
                unmatched_fonts.append(font_metadata.filename)

        if unmatched_fonts:
            msg = 'Unmatched family name are in fonts: {}'
            self.fail(msg.format(', '.join(unmatched_fonts)))


class TestPostScriptNameInMetadataEqualFontOnDisk(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required')
    def test_postscriptname_in_metadata_equal_to_font_on_disk(self):
        """ Checks METADATA.json 'postScriptName' matches TTF 'postScriptName' """
        contents = self.read_metadata_contents()
        metadata = Metadata.get_family_metadata(contents)

        for font_metadata in metadata.fonts:
            try:
                font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            except IOError:
                continue
            if font.post_script_name != font_metadata.post_script_name:

                msg = 'In METADATA postScriptName="{0}", but in TTF "{1}"'
                self.fail(msg.format(font.post_script_name,
                                     font_metadata.post_script_name))


class CheckMetadataAgreements(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def setUp(self):
        contents = self.read_metadata_contents()
        self.metadata = Metadata.get_family_metadata(contents)

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_metadata_family_values_are_all_the_same(self):
        """ Check that METADATA family values are all the same """
        name = ''
        for font_metadata in self.metadata.fonts:
            if name and font_metadata.name != name:
                self.fail('Family name in metadata fonts items not the same')
            name = font_metadata.name

    def test_metadata_font_have_regular(self):
        """ According GWF standarts font should have Regular style. """
        # this tests will appear in each font
        have = False
        for i in self.metadata.fonts:
            if i.weight == 400 and i.style == 'normal':
                have = True

        self.assertTrue(have)

    @tags('required')
    def test_metadata_regular_is_400(self):
        """ Regular should be 400 """
        have = False
        for i in self.metadata.fonts:
            if i.filename.endswith('Regular.ttf') and i.weight == 400:
                have = True
        if not have:
            self.fail(('METADATA.json does not contain Regular font. At least'
                       ' one font must be Regular and its weight must be 400'))

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        have = False
        for x in self.metadata.fonts:
            if x.full_name.endswith('Regular') and x.style == 'normal':
                have = True
        self.assertTrue(have)

    @tags('required')
    def test_metadata_filename_matches_postscriptname(self):
        """ METADATA.json `filename` matches `postScriptName` """
        import re
        regex = re.compile(r'\W')

        for x in self.metadata.fonts:
            post_script_name = regex.sub('', x.post_script_name)
            filename = regex.sub('', os.path.splitext(x.filename)[0])
            if filename != post_script_name:
                msg = '"{0}" does not match "{1}"'
                self.fail(msg.format(x.filename, x.post_script_name))

    @tags('required')
    def test_metadata_fullname_matches_postScriptName(self):
        """ METADATA.json `fullName` matches `postScriptName` """
        import re
        regex = re.compile(r'\W')

        for x in self.metadata.fonts:
            post_script_name = regex.sub('', x.post_script_name)
            fullname = regex.sub('', x.full_name)
            if fullname != post_script_name:
                msg = '"{0}" does not match "{1}"'
                self.fail(msg.format(x.full_name, x.post_script_name))

    def test_metadata_fullname_is_equal_to_internal_font_fullname(self):
        """ METADATA.json 'fullname' value matches internal 'fullname' """
        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            self.assertEqual(font.fullname, font_metadata.full_name)

    def test_font_name_matches_family(self):
        """ METADATA.json fonts 'name' property should be
            same as font familyname """

        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if font_metadata.name != font.familyname:
                msg = '"fonts.name" property is not the same as TTF familyname'
                self.fail(msg)

    def test_metadata_fonts_fields_have_fontname(self):
        """ METADATA.json fonts items fields "name", "postScriptName",
            "fullName", "filename" contains font name right format """
        for x in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, x)

            self.assertIn(font.familyname, x.name)
            self.assertIn(font.familyname, x.full_name)
            self.assertIn("".join(str(font.familyname).split()),
                          x.filename)
            self.assertIn("".join(str(font.familyname).split()),
                          x.post_script_name)


class CheckMetadataContainsReservedFontName(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('info')
    def test_copyright_contains_correct_rfn(self):
        """ Copyright notice does not contain Reserved File Name """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            if 'Reserved Font Name' in font_metadata.copyright:
                msg = '"%s" contains "Reserved File Name"'
                self.fail(msg % font_metadata.copyright)

    @tags('info')
    def test_copyright_matches_pattern(self):
        """ Copyright notice matches canonical pattern """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            self.assertRegexpMatches(font_metadata.copyright,
                                     r'Copyright\s+\(c\)\s+20\d{2}.*\(.*@.*.*\)')

    @tags('info')
    def test_copyright_is_consistent_across_family(self):
        """ Copyright notice is the same in all fonts? """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        copyright = ''
        for font_metadata in fm.fonts:
            if copyright and font_metadata.copyright != copyright:
                self.fail('Copyright is inconsistent across family')
            copyright = font_metadata.copyright

    @tags('info')
    def test_metadata_copyright_size(self):
        """ Copyright notice should be less than 500 chars """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            self.assertLessEqual(len(font_metadata.copyright), 500)


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


class File(object):

    def __init__(self, rootdir):
        self.rootdir = rootdir

    def exists(self, filename):
        return op.exists(op.join(self.rootdir, filename))

    def size(self, filename):
        return op.getsize(op.join(self.rootdir, filename))

    def mime(self, filename):
        return magic.from_file(op.join(self.rootdir, filename), mime=True)


class CheckSubsetsExist(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def setUp(self):
        self.f = File(op.dirname(self.operator.path))

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def get_subset_filename(self, font_filename, subset_name):
        return font_filename.replace('.ttf', '.%s' % subset_name)

    def test_check_subsets_exists(self):
        """ Check that corresponding subset files exist for fonts """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            for subset in fm.subsets:
                subset_filename = self.get_subset_filename(font_metadata.filename, subset)

                error = "The subset file for the %s subset does not exist"
                error = error % subset_filename
                self.assertTrue(self.f.exists(subset_filename), error)

                error = "The subset file %s is bigger than the original file"
                error = error % subset_filename
                self.assertLessEqual(self.f.size(subset_filename),
                                     self.f.size(font_metadata.filename),
                                     error)

                self.assertEqual(self.f.mime(subset_filename),
                                 'application/x-font-ttf')


class CheckMonospaceAgreement(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_monospace_agreement(self):
        """ Monospace font has hhea.advanceWidthMax equal to each
            glyph advanceWidth """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        if fm.category != 'Monospace':
            return
        for font_metadata in fm.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path,
                                                 font_metadata.filename)
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    self.fail(('Glyph advanceWidth must be same'
                               ' across all glyphs %s' % prev))
                prev = font.advance_width(g)

            if prev != font.advance_width():
                msg = ('"hhea" table advanceWidthMax property differs'
                       ' to glyphs advanceWidth [%s, %s]')
                self.fail(msg % (prev, font.advance_width()))


class CheckItalicStyleMatchesMacStyle(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_italic_style_matches_names(self):
        """ Check metadata.json font.style `italic` matches font internal """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

        for font_metadata in family.fonts:
            if font_metadata.style != 'italic':
                continue

            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            if not bool(font.macStyle & 0b10):
                self.fail(('Metadata style has been set to italic'
                           ' but font second bit in macStyle has'
                           ' not been set'))

            style = font.familyname.split('-')[-1]
            if not style.endswith('Italic'):
                self.fail(('macStyle second bit is set but postScriptName "%s"'
                           ' is not ended with "Italic"') % font.familyname)

            style = font.fullname.split('-')[-1]
            if not style.endswith('Italic'):
                self.fail(('macStyle second bit is set but fullName "%s"'
                           ' is not ended with "Italic"') % font.fullname)


class CheckNormalStyleMatchesMacStyle(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_normal_style_matches_names(self):
        """ Check metadata.json font.style `italic` matches font internal """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

        for font_metadata in family.fonts:
            if font_metadata.style != 'normal':
                continue

            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            if bool(font.macStyle & 0b10):
                self.fail(('Metadata style has been set to normal'
                           ' but font second bit (italic) in macStyle has'
                           ' been set'))

            style = font.familyname.split('-')[-1]
            if style.endswith('Italic'):
                self.fail(('macStyle second bit is not set but postScriptName "%s"'
                           ' is ended with "Italic"') % font.familyname)

            style = font.fullname.split('-')[-1]
            if style.endswith('Italic'):
                self.fail(('macStyle second bit is not set but fullName "%s"'
                           ' is ended with "Italic"') % font.fullname)


class CheckMetadataMatchesNameTable(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_metadata_matches_nametable(self):
        """ Metadata key-value match to table name fields """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            report = '%s: Family name was supposed to be "%s" but is "%s"'
            report = report % (font_metadata.name, fm.name,
                               ttfont.familyname)
            self.assertEqual(ttfont.familyname, fm.name, report)
            self.assertEqual(ttfont.fullname, font_metadata.full_name)


class CheckMetadataFields(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required')
    def test_check_metadata_fields(self):
        """ Check METADATA.json "fonts" property items have required field """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

        keys = [("name", str), ("postScriptName", str),
                ("fullName", str), ("style", str),
                ("weight", int), ("filename", str),
                ("copyright", str)]

        missing = set([])
        unknown = set([])

        for j, itemtype in keys:

            for font_metadata in family.fonts:
                if j not in font_metadata:
                    missing.add(j)

                for k in font_metadata:
                    if k not in map(lambda x: x[0], keys):
                        unknown.add(k)

        if unknown:
            msg = 'METADATA.json "fonts" property has unknown items [%s]'
            self.fail(msg % ', '.join(unknown))

        if missing:
            msg = 'METADATA.json "fonts" property items missed [%s] items'
            self.fail(msg % ', '.join(missing))


class CheckMenuSubsetContainsProperGlyphs(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_menu_contains_proper_glyphs(self):
        """ Check menu file contains proper glyphs """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            tf = Font.get_ttfont_from_metadata(self.operator.path, font_metadata, is_menu=True)
            self.check_retrieve_glyphs(tf, font_metadata)

    def check_retrieve_glyphs(self, ttfont, font_metadata):
        cmap = ttfont.retrieve_cmap_format_4()

        glyphs = cmap.cmap

        missing_glyphs = set()
        if ord(' ') not in glyphs:
            missing_glyphs.add(' ')

        for g in font_metadata.name:
            if ord(g) not in glyphs:
                missing_glyphs.add(g)

        if missing_glyphs:
            _ = '%s: Menu is missing glyphs: "%s"'
            report = _ % (font_metadata.filename, ''.join(missing_glyphs))
            self.fail(report)


class CheckGlyphConsistencyInFamily(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def setUp(self):
        contents = self.read_metadata_contents()
        self.familymetadata = Metadata.get_family_metadata(contents)

    def test_the_same_number_of_glyphs_across_family(self):
        """ The same number of glyphs across family? """
        glyphs_count = 0
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if not glyphs_count:
                glyphs_count = len(ttfont.glyphs)

            if glyphs_count != len(ttfont.glyphs):
                self.fail('Family has a different glyphs\'s count in fonts')

    def test_the_same_names_of_glyphs_across_family(self):
        """ The same names of glyphs across family? """
        glyphs = None
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if not glyphs:
                glyphs = len(ttfont.glyphs)

            if glyphs != len(ttfont.glyphs):
                self.fail('Family has a different glyphs\'s names in fonts')

    def test_the_same_encodings_of_glyphs_across_family(self):
        """ The same unicode encodings of glyphs across family? """
        encoding = None
        for font_metadata in self.familymetadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            cmap = ttfont.retrieve_cmap_format_4()

            if not encoding:
                encoding = cmap.platEncID

            if encoding != cmap.platEncID:
                self.fail('Family has different encoding across fonts')


class CheckFontNameNotInCamelCase(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_fontname_not_in_camel_case(self):
        """ Check if fontname is not camel cased """
        contents = self.read_metadata_contents()
        familymetadata = Metadata.get_family_metadata(contents)

        camelcased_fontnames = []
        for font_metadata in familymetadata.fonts:
            if bool(re.match(r'([A-Z][a-z]+){2,}', font_metadata.name)):
                camelcased_fontnames.append(font_metadata.name)

        if camelcased_fontnames:
            self.fail(('%s are camel cased names. To solve this check just '
                       'use spaces in names.'))


class CheckFontsMenuAgreements(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def menufile(self, font_metadata):
        return '%s.menu' % font_metadata.filename[:-4]

    @tags('required')
    def test_menu_file_agreement(self):
        """ Check fonts have corresponding menu files """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            menufile = self.menufile(font_metadata)
            path = op.join(op.dirname(self.operator.path), menufile)

            if not op.exists(path):
                self.fail('%s does not exist' % menufile)

            if magic.from_file(path) != 'TrueType font data':
                self.fail('%s is not actual TTF file' % menufile)


class CheckFamilyNameMatchesFontNames(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_familyname_matches_fontnames(self):
        """ Check font name is the same as family name """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            _ = '%s: Family name "%s" does not match font name: "%s"'
            _ = _ % (font_metadata.filename, fm.name, font_metadata.name)
            self.assertEqual(font_metadata.name, fm.name, _)


weights = {
    'Thin': 100,
    'ThinItalic': 100,
    'ExtraLight': 200,
    'ExtraLightItalic': 200,
    'Light': 300,
    'LightItalic': 300,
    'Regular': 400,
    'Italic': 400,
    'Medium': 500,
    'MediumItalic': 500,
    'SemiBold': 600,
    'SemiBoldItalic': 600,
    'Bold': 700,
    'BoldItalic': 700,
    'ExtraBold': 800,
    'ExtraBoldItalic': 800,
    'Black': 900,
    'BlackItalic': 900,
}


class CheckCanonicalWeights(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_canonical_weights(self):
        """ Check that weights have canonical value """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            weight = font_metadata.weight
            first_digit = weight / 100
            is_invalid = (weight % 100) != 0 or (first_digit < 1
                                                 or first_digit > 9)
            _ = ("%s: The weight is %d which is not a "
                 "multiple of 100 between 1 and 9")

            self.assertFalse(is_invalid, _ % (op.basename(self.operator.path),
                                              font_metadata.weight))

            tf = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            _ = ("%s: METADATA.json overwrites the weight. "
                 " The METADATA.json weight is %d and the font"
                 " file %s weight is %d")
            _ = _ % (font_metadata.filename, font_metadata.weight,
                     font_metadata.filename, tf.OS2_usWeightClass)

            self.assertEqual(tf.OS2_usWeightClass, font_metadata.weight)


class CheckPostScriptNameMatchesWeight(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_postscriptname_contains_correct_weight(self):
        """ Metadata weight matches postScriptName """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            pair = []
            for k, weight in weights.items():
                if weight == font_metadata.weight:
                    pair.append((k, weight))

            if not pair:
                self.fail('Font weight does not match for "postScriptName"')

            if not (font_metadata.post_script_name.endswith('-%s' % pair[0][0])
                    or font_metadata.post_script_name.endswith('-%s' % pair[1][0])):

                _ = ('postScriptName with weight %s must be '
                     'ended with "%s" or "%s"')
                self.fail(_ % (pair[0][1], pair[0][0], pair[1][0]))


class CheckFontWeightSameAsInMetadata(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_font_weight_same_as_in_metadata(self):
        """ Font weight matches metadata.json value of key "weight" """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:

            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
            if font.OS2_usWeightClass != font_metadata.weight:
                msg = 'METADATA.JSON has weight %s but in TTF it is %s'
                self.fail(msg % (font_metadata.weight, font.OS2_usWeightClass))


class CheckFullNameEqualCanonicalName(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_metadata_contains_current_font(self):
        """ METADATA.json should contains testing font, under canonic name"""

        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        is_canonical = False
        for font_metadata in fm.fonts:
            font = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)

            _weights = []
            for value, intvalue in weights.items():
                if intvalue == font.OS2_usWeightClass:
                    _weights.append(value)

            for w in _weights:
                current_font = "%s %s" % (font.familyname, w)
                if font_metadata.full_name != current_font:
                    is_canonical = True

            if not is_canonical:
                v = map(lambda x: font.familyname + ' ' + x, _weights)
                msg = 'Canonical name in font expected: [%s] but %s'
                self.fail(msg % (v, font_metadata.full_name))


class CheckCanonicalStyles(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    CANONICAL_STYLE_VALUES = ['italic', 'normal']
    ITALIC_MASK = 0b10

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_check_canonical_styles(self):
        """ Test If font styles are canonical """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            self.assertIn(font_metadata.style, self.CANONICAL_STYLE_VALUES)
            if self.is_italic(font_metadata):
                if font_metadata.style != 'italic':
                    _ = "%s: The font style is %s but it should be italic"
                    self.fail(_ % (font_metadata.filename, font_metadata.style))
            else:
                if font_metadata.style != 'normal':
                    _ = "%s: The font style is %s but it should be normal"
                    self.fail(_ % (font_metadata.filename, font_metadata.style))

    def is_italic(self, font_metadata):
        ttfont = Font.get_ttfont_from_metadata(self.operator.path, font_metadata)
        return (ttfont.macStyle & self.ITALIC_MASK
                or ttfont.italicAngle
                or self.find_italic_in_name_table(ttfont))

    def find_italic_in_name_table(self, ttfont):
        for entry in ttfont.names:
            if 'italic' in Font.bin2unistring(entry).lower():
                return True


class CheckCanonicalFilenames(TestCase):
    weights = {
        100: 'Thin',
        200: 'ExtraLight',
        300: 'Light',
        400: '',
        500: 'Medium',
        600: 'SemiBold',
        700: 'Bold',
        800: 'ExtraBold',
        900: 'Black'
    }

    style_names = {
        'normal': '',
        'italic': 'Italic'
    }

    name = __name__
    tool = 'lint'
    targets = ['metadata']

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    @tags('required')
    def test_check_canonical_filenames(self):
        """ Test If filename is canonical """
        contents = self.read_metadata_contents()
        family_metadata = Metadata.get_family_metadata(contents)
        for font_metadata in family_metadata.fonts:
            canonical_filename = self.create_canonical_filename(font_metadata)
            self.assertEqual(canonical_filename, font_metadata.filename)

    def create_canonical_filename(self, font_metadata):
        familyname = font_metadata.name.replace(' ', '')
        style_weight = '%s%s' % (self.weights.get(font_metadata.weight),
                                 self.style_names.get(font_metadata.style))
        if not style_weight:
            style_weight = 'Regular'
        return '%s-%s.ttf' % (familyname, style_weight)
