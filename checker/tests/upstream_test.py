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

from checker.base import BakeryTestCase as TestCase, tags
from fontaine.font import FontFactory
from fontaine.cmap import Library


class ProjectUpstreamTestCase(TestCase):
    """ Common tests for upstream repository.

    .. note::

    This test case is not related to font processing. It makes only common
    checks like one - test that upstream repository contains bakery.yaml) """

    targets = ['upstream-repo']
    tool = 'FontBakery'
    path = '.'
    name = __name__

    @tags('note')
    def test_bakery_yaml_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'bakery.yaml')),
                        msg=('File `bakery.yaml` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_fontlog_txt_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'FONTLOG.txt')),
                        msg=('File `FONTLOG.txt` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_description_html_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'DESCRIPTION.en_us.html')),
                        msg=('File `DESCRIPTION.en_us.html` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_metadata_json_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'METADATA.json')),
                        msg=('File `METADATA.json` does not exist in root '
                             'of upstream repository'))

    def test_copyright_notices_same_across_family(self):
        """ Are all copyright notices the same in all styles? """
        ufo_dirs = []
        for root, dirs, files in os.walk(self.path):
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

        while os.path.realpath(self.path) != current_path:
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


COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)


def get_test_subset_function(value):
    def function(self):
        self.assertEqual(value, 100)
    function.tags = ['note']
    return function


def get_sources_lists(rootpath):
    """ Return list of lists of UFO, TTX and METADATA.json """
    ufo_dirs = []
    ttx_files = []
    metadata_files = []
    l = len(rootpath)
    for root, dirs, files in os.walk(rootpath):
        for f in files:
            fullpath = op.join(root, f)
            if op.splitext(fullpath[l:])[1].lower() in ['.ttx', ]:
                if fullpath[l:].count('.') > 1:
                    continue
                ttx_files.append(fullpath[l:])
            if f.lower() == 'metadata.json':
                metadata_files.append(fullpath[:l])
        for d in dirs:
            fullpath = op.join(root, d)
            if op.splitext(fullpath)[1].lower() == '.ufo':
                ufo_dirs.append(fullpath[l:])
    return ufo_dirs, ttx_files, metadata_files


class FontaineTest(TestCase):

    targets = ['upstream-repo']
    tool = 'PyFontaine'
    name = __name__
    path = '.'

    @classmethod
    def __generateTests__(cls):
        pattern = re.compile('[\W_]+')
        library = Library(collections=['subsets'])
        ufo_files, ttx_files, _ = get_sources_lists(cls.path)
        for fontpath in ufo_files + ttx_files:
            font = FontFactory.openfont(fontpath)
            for charmap, _, coverage, _ in \
                    font.get_orthographies(_library=library):
                common_name = charmap.common_name.replace('Subset ', '')
                shortname = pattern.sub('', common_name)
                exec 'cls.test_charset_%s = get_test_subset_function(%s)' % (shortname, coverage)
                exec 'cls.test_charset_%s.__func__.__doc__ = "Is %s covered 100%%?"' % (shortname, common_name)


import fontforge
from fontTools.ttLib import TTFont


class UFO_FontFamilyNamingTest(TestCase):

    targets = ['upstream']
    tool = 'FontForge'
    name = __name__
    path = '.'

    def test_ufo_family_naming_recommendation(self):
        """ The font corresponds the font family naming recommendation.
        See http://forum.fontlab.com/index.php?topic=313.0 """
        if self.path.lower().endswith('.ttx'):
            # This test checks only UFO source font.
            # To see
            return
        font = fontforge.open(self.path)
        # <Full name> limitation is < 64 chars
        length = len(font.sfnt_names[4][2])
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        # <Postscript name> limitation is < 30 chars
        length = len(font.sfnt_names[6][2])
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        # <Postscript name> may contain only a-zA-Z0-9
        # and one hyphen
        self.assertRegexpMatches(font.sfnt_names[6][2], r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(font.sfnt_names[6][2].count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        # <Family Name> limitation is 32 chars
        length = len(font.sfnt_names[1][2])
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Style Name> limitation is 32 chars
        length = len(font.sfnt_names[2][2])
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Weight> value >= 250 and <= 900 in steps of 50
        self.assertTrue(bool(font.os2_weight % 50 == 0),
                        msg=('Weight has to be in steps of 50.'
                             ' Now: %s') % font.os2_weight)

        self.assertGreaterEqual(font.os2_weight, 250)
        self.assertLessEqual(font.os2_weight, 900)


def bin2unistring(record):
    if b'\000' in record.string:
        string = record.string.decode('utf-16-be')
        return string.encode('utf-8')
    else:
        return record.string


def get_name_record(records, nameid, platform, platencid, language):
    for record in records:
        if (record.nameID == nameid
                and record.platformID == platform
                and record.langID == language
                and record.platEncID == platencid):
            return record


class TTX_FontFamilyNamingTest(TestCase):

    targets = ['upstream-ttx']
    path = '.'
    name = __name__
    tool = 'TTFont'

    def test_ttx_family_naming_recommendation(self):
        """ The font corresponds the font family naming recommendation.
        See http://forum.fontlab.com/index.php?topic=313.0 """
        if not self.path.lower().endswith('.ttx'):
            return
        font = TTFont(None)
        font.importXML(self.path, quiet=True)

        names = font['name'].names
        # <Full name> limitation is < 64 chars
        length = len(bin2unistring(get_name_record(names, 4, 1, 0, 0)))
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        length = len(bin2unistring(get_name_record(names, 4, 3, 1, 1033)))
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        # <Postscript name> limitation is < 30 chars
        length = len(bin2unistring(get_name_record(names, 6, 1, 0, 0)))
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        length = len(bin2unistring(get_name_record(names, 6, 3, 1, 1033)))
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        # <Postscript name> may contain only a-zA-Z0-9
        # and one hyphen
        name = bin2unistring(get_name_record(names, 6, 1, 0, 0))
        self.assertRegexpMatches(name, r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(name.count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        name = bin2unistring(get_name_record(names, 6, 3, 1, 1033))
        self.assertRegexpMatches(name, r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(name.count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        # <Family Name> limitation is 32 chars
        length = len(bin2unistring(get_name_record(names, 1, 1, 0, 0)))
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        length = len(bin2unistring(get_name_record(names, 1, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Style Name> limitation is 32 chars
        length = len(bin2unistring(get_name_record(names, 2, 1, 0, 0)))
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        length = len(bin2unistring(get_name_record(names, 2, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Family Name> limitation is 32 chars
        length = len(bin2unistring(get_name_record(names, 16, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Style Name> limitation is 32 chars
        length = len(bin2unistring(get_name_record(names, 17, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        if 'OS/2' in font.tables:
            # <Weight> value >= 250 and <= 900 in steps of 50
            self.assertTrue(bool(font['OS/2'].usWeightClass % 50 == 0),
                            msg=('OS/2 usWeightClass has to be in steps of 50.'
                                 ' Now: %s') % font['OS/2'].usWeightClass)

            self.assertGreaterEqual(font['OS/2'].usWeightClass, 250)
            self.assertLessEqual(font['OS/2'].usWeightClass, 900)

        if 'CFF' in font.tables:
            self.assertTrue(bool(font['CFF'].Weight % 50 == 0),
                            msg=('CFF Weight has to be in steps of 50.'
                                 ' Now: %s') % font['CFF'].Weight)

            self.assertGreaterEqual(font['CFF'].Weight, 250)
            self.assertLessEqual(font['CFF'].Weight, 900)


import robofab.world
import robofab.objects


class UfoOpenTest(TestCase):
    targets = ['upstream']
    tool = 'Robofab'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = robofab.world.OpenFont(self.path)
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    def test_it_exists(self):
        """ Does this UFO path exist? """
        self.assertEqual(os.path.exists(self.path), True)

    def test_is_folder(self):
        """ Is this UFO really a folder?"""
        self.assertEqual(os.path.isdir(self.path), True)

    def test_is_ended_ufo(self):
        """ Does this font file's name end with '.ufo'?"""
        self.assertEqual(self.path.lower().endswith('.ufo'), True)

    # @tags('required')
    def test_is_A(self):
        """ Does this font have a glyph named 'A'?"""
        self.assertTrue('A' in self.font)

    def test_is_A_a_glyph_instance(self):
        """ Is this font's property A an instance of an RGlyph object? """
        if 'A' in self.font:
            a = self.font['A']
        else:
            a = None
        self.assertIsInstance(a, robofab.objects.objectsRF.RGlyph)

    def test_is_fsType_eq_1(self):
        """Is the OS/2 table fsType set to 0?"""
        desiredFsType = [0]
        self.assertEqual(self.font.info.openTypeOS2Type, desiredFsType)

    # TODO check if this is a good form of test
    def has_character(self, unicodeString):
        """Does this font include a glyph for the given unicode character?"""
        # TODO check the glyph has at least 1 contour
        character = unicodeString[0]
        glyph = None
        if character in self.font:
            glyph = self.font[character]
        self.assertIsInstance(glyph, robofab.objects.objectsRF.RGlyph)

    def test_has_rupee(self):
        u""" Does this font include a glyph for ₹, the Indian Rupee Sign
             codepoint?"""
        self.has_character(self, u'₹')
