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
import glob
import os
import os.path as op
import re
import yaml

from fontaine.font import FontFactory
from fontaine.cmap import Library

from bakery_cli.ttfont import PiFont
from bakery_cli.utils import UpstreamDirectory
from bakery_lint.base import BakeryTestCase as TestCase, tags, \
    TestCaseOperator


COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)


class FontTestPrepolation(TestCase):

    name = __name__
    targets = ['upstream-repo']
    tool = 'lint'

    def test_family_glyph_names_match(self):
        """ Each font in family has matching glyph names? """
        directory = UpstreamDirectory(self.operator.path)
        # TODO does this glyphs list object get populated?
        glyphs = []
        for f in directory.get_fonts():
            font = PiFont(op.join(self.operator.path, f))
            glyphs_ = font.get_glyphs()

            if glyphs and glyphs != glyphs_:
                # TODO report which font
                self.fail('Family has different glyphs across fonts')

    def test_font_prepolation_glyph_contours(self):
        """ Check that glyphs has same number of contours across family """
        directory = UpstreamDirectory(self.operator.path)

        glyphs = {}
        for f in directory.get_fonts():
            font = PiFont(op.join(self.operator.path, f))
            glyphs_ = font.get_glyphs()

            for glyphcode, glyphname in glyphs_:
                contours = font.get_contours_count(glyphname)
                if glyphcode in glyphs and glyphs[glyphcode] != contours:
                    msg = ('Number of contours of glyph "%s" does not match.'
                           ' Expected %s contours, but actual is %s contours')
                    self.fail(msg % (glyphname, glyphs[glyphcode], contours))
                glyphs[glyphcode] = contours

    def test_font_prepolation_glyph_points(self):
        """ Check that glyphs has same number of points across family """
        directory = UpstreamDirectory(self.operator.path)

        glyphs = {}
        for f in directory.get_fonts():
            font = PiFont(op.join(self.operator.path, f))
            glyphs_ = font.get_glyphs()

            for g, glyphname in glyphs_:
                points = font.get_points_count(glyphname)
                if g in glyphs and glyphs[g] != points:
                    msg = ('Number of points of glyph "%s" does not match.'
                           ' Expected %s points, but actual is %s points')
                    self.fail(msg % (glyphname, glyphs[g], points))
                glyphs[g] = points


class TestTTFAutoHintHasDeva(TestCase):

    targets = ['upstream-repo']
    tool = 'lint'
    name = __name__

    @classmethod
    def skipUnless(cls):
        projroot = os.path.join(cls.operator.path, '..')
        bakeryconfig = None

        bakeryfile = os.path.join(projroot, 'bakery.yaml')
        if os.path.exists(bakeryfile):
            bakeryconfig = yaml.load(open(bakeryfile))

        bakeryfile = os.path.join(projroot, 'bakery.yml')
        if os.path.exists(bakeryfile):
            bakeryconfig = yaml.load(open(bakeryfile))

        if bakeryconfig is None:
            return True

        if 'devanagari' not in bakeryconfig.get('subset', []):
            return True

        cls.bakeryconfig = bakeryconfig

    def test_ttfautohint_has_deva(self):
        """ Check that ttfautohint option has -f deva with devanagari subset """
        if '-f deva' not in self.bakeryconfig.get('ttfautohint', ''):
            self.fail((u'Subset `devanagari` is selected but ttfautohint'
                       u' does not have `-f deva` option'))


class TestUpstreamRepo(TestCase):
    """ Tests for common upstream repository files.

    .. note::

    This test case is not related to font processing. It makes only common
    checks like one - test that upstream repository contains bakery.yaml) """

    targets = ['upstream-repo']
    tool = 'lint'
    name = __name__

    @tags('note')
    def test_bakery_yaml_exists(self):
        """ Repository contains bakery.yaml configuration file? """
        f = os.path.exists(os.path.join(self.operator.path, '..', 'bakery.yaml'))
        f = f or os.path.exists(os.path.join(self.operator.path, '..', 'bakery.yml'))
        self.assertTrue(f,
                        msg=('File `bakery.yaml` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_fontlog_txt_exists(self):
        """ Repository contains FONTLOG.txt file? """
        self.assertTrue(os.path.exists(os.path.join(self.operator.path, '..', 'FONTLOG.txt')),
                        msg=('File `FONTLOG.txt` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_description_html_exists(self):
        """ Repository contains DESCRIPTION.en_us.html file? """
        self.assertTrue(os.path.exists(os.path.join(self.operator.path, '..', 'DESCRIPTION.en_us.html')),
                        msg=('File `DESCRIPTION.en_us.html` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_metadata_json_exists(self):
        """ Repository contains METADATA.json file? """
        self.assertTrue(os.path.exists(os.path.join(self.operator.path, '..', 'METADATA.json')),
                        msg=('File `METADATA.json` does not exist in root '
                             'of upstream repository'))

    def test_copyright_notices_same_across_family(self):
        """ Each font copyright notice matches? """
        ufo_dirs = []
        for root, dirs, files in os.walk(self.operator.path):
            for d in dirs:
                fullpath = os.path.join(root, d)
                if os.path.splitext(fullpath)[1].lower() == '.ufo':
                    ufo_dirs.append(fullpath)

        copyright = None
        for ufo_folder in ufo_dirs:
            current_notice = self.lookup_copyright_notice(ufo_folder)
            if current_notice is None:
                continue
            if copyright is not None and current_notice != copyright:
                self.fail('"%s" != "%s"' % (current_notice, copyright))
                break
            copyright = current_notice

    def grep_copyright_notice(self, contents):
        match = COPYRIGHT_REGEX.search(contents)
        if match:
            return match.group(0).strip(',\r\n')
        return

    def lookup_copyright_notice(self, ufo_folder):
        current_path = ufo_folder
        try:
            contents = open(os.path.join(ufo_folder, 'fontinfo.plist')).read()
            copyright = self.grep_copyright_notice(contents)
            if copyright:
                return copyright
        except (IOError, OSError):
            pass

        while os.path.realpath(self.operator.path) != current_path:
            # look for all text files inside folder
            # read contents from them and compare with copyright notice
            # pattern
            files = glob.glob(os.path.join(current_path, '*.txt'))
            files += glob.glob(os.path.join(current_path, '*.ttx'))
            for filename in files:
                with open(os.path.join(current_path, filename)) as fp:
                    match = COPYRIGHT_REGEX.search(fp.read())
                    if not match:
                        continue
                    return match.group(0).strip(',\r\n')
            current_path = os.path.join(current_path, '..')  # go up
            current_path = os.path.realpath(current_path)
        return


def get_test_subset_function(value):
    def function(self):
        self.assertEqual(value, 100)
    function.tags = ['note']
    return function


class FontaineTest(TestCase):

    targets = ['upstream-repo']
    tool = 'PyFontaine'
    name = __name__

    @classmethod
    def __generateTests__(cls):
        pattern = re.compile(r'[\W_]+')
        library = Library(collections=['subsets'])

        directory = UpstreamDirectory(cls.operator.path)

        yamlpath = op.join(cls.operator.path, 'bakery.yaml')
        try:
            bakerydata = yaml.load(open(yamlpath))
        except IOError:
            from bakery_cli.bakery import BAKERY_CONFIGURATION_DEFAULTS
            bakerydata = yaml.load(open(BAKERY_CONFIGURATION_DEFAULTS))

        for fontpath in directory.UFO + directory.TTX:
            font = FontFactory.openfont(op.join(cls.operator.path, fontpath))
            for charmap in font.get_orthographies(_library=library):
                common_name = charmap.charmap.common_name.replace('Subset ', '')
                shortname = pattern.sub('', common_name)
                if shortname not in bakerydata['subset']:
                    continue

                exec 'cls.test_charset_%s = get_test_subset_function(%s)' % (shortname, charmap.coverage)
                exec 'cls.test_charset_%s.__func__.__doc__ = "Is %s covered 100%%?"' % (shortname, common_name)


def get_suite(path, apply_autofix=False):
    import unittest
    suite = unittest.TestSuite()

    testcases = [
        FontTestPrepolation,
        TestTTFAutoHintHasDeva,
        TestUpstreamRepo,
        FontaineTest
    ]

    for testcase in testcases:

        testcase.operator = TestCaseOperator(path)
        testcase.apply_fix = apply_autofix

        if getattr(testcase, 'skipUnless', False):
            if testcase.skipUnless():
                continue

        if getattr(testcase, '__generateTests__', None):
            testcase.__generateTests__()
        
        for test in unittest.defaultTestLoader.loadTestsFromTestCase(testcase):
            suite.addTest(test)

    return suite