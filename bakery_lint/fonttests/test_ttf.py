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
import fontforge
import magic
import os
import os.path
import re
import StringIO
import sys
import unicodedata


from contextlib import contextmanager
from fontTools import ttLib

from bakery_lint.base import BakeryTestCase as TestCase, tags, autofix, \
    TestCaseOperator
from bakery_cli.fixers import OFLLicenseInfoURLFixer, ApacheLicenseInfoURLFixer, \
    OFLLicenseDescriptionFixer, ApacheLicenseDescriptionFixer
from bakery_cli.fixers import CharacterSymbolsFixer
from bakery_cli.fixers import get_unencoded_glyphs
from bakery_cli.ttfont import Font, FontTool, getSuggestedFontNameValues
from bakery_cli.utils import run, UpstreamDirectory
from bakery_cli.nameid_values import *

@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


def getNameRecordValue(nameRecord):
    return nameRecord.string.decode(nameRecord.getEncoding())


class TTFTestCase(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    def test_fontforge_openfile_contains_stderr(self):
        with redirect_stdout(StringIO.StringIO()) as std:
            fontforge.open(self.operator.path)
            if std.getvalue():
                self.fail('FontForge prints STDERR')

    @autofix('bakery_cli.fixers.OpentypeFamilyNameFixer')
    def test_check_opentype_familyname(self):
        """ FamilyName matches Windows-only Opentype-specific FamilyName? """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_family_name, font.familyname)

    @autofix('bakery_cli.fixers.OpentypeFullnameFixer')
    def test_check_opentype_fullname(self):
        """ Fullname matches Windows-only Opentype-specific Fullname? """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_full_name, font.fullname)

    @autofix('bakery_cli.fixers.SubfamilyNameFixer')
    def test_suggested_subfamily_name(self):
        """ Family and style names are set canonically? """
        font = Font.get_ttfont(self.operator.path)
        suggestedvalues = getSuggestedFontNameValues(font.ttfont)
        self.assertEqual(font.familyname, suggestedvalues['family'])
        self.assertEqual(font.stylename, suggestedvalues['subfamily'])

    def test_check_os2_width_class(self):
        """ OS/2 width class is correctly set? """
        font = Font.get_ttfont(self.operator.path)
        error = "OS/2 widthClass must be [1..9] inclusive, was %s IE9 fail"
        error = error % font.OS2_usWidthClass
        self.assertIn(font.OS2_usWidthClass, range(1, 10), error)

    def test_check_upm_heigths_less_120(self):
        """ UPM Heights are NOT greater than 120%? """
        ttfont = Font.get_ttfont(self.operator.path)
        value = ttfont.ascents.get_max() + abs(ttfont.descents.get_min())
        value = value * 100 / float(ttfont.get_upm_height())
        if value > 120:
            _ = "UPM:Height is %d%%, consider redesigning to 120%% or less"
            self.fail(_ % value)


