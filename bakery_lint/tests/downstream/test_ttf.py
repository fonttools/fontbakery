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
import os
import os.path
import re
import StringIO
import sys

from contextlib import contextmanager

from bakery_lint.base import BakeryTestCase as TestCase, autofix
from bakery_cli.ttfont import Font, getSuggestedFontNameValues


@contextmanager
def redirect_stdout(new_target):
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


class TTXTestCase(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    def test_fontforge_openfile_contains_stderr(self):
        with redirect_stdout(StringIO.StringIO()) as std:
            fontforge.open(self.operator.path)
            if std.getvalue():
                self.fail('FontForge prints STDERR')

    @autofix('bakery_cli.pipe.autofix.rename')
    def test_source_ttf_font_filename_equals_familystyle(self):
        """ Source TTF Font filename equals family style """
        ttfont = Font.get_ttfont(self.operator.path)

        suggestedvalues = getSuggestedFontNameValues(ttfont.ttfont)

        family_name = suggestedvalues['family']
        subfamily_name = suggestedvalues['subfamily']

        expectedname = '{0}-{1}'.format(family_name.replace(' ', ''),
                                        subfamily_name.replace(' ', ''))
        actualname, extension = os.path.splitext(self.operator.path)

        expected_filename = '{0}{1}'.format(expectedname, extension)
        setattr(self, 'expectedfilename', expected_filename)
        self.assertEqual(os.path.basename(actualname), expectedname)

    def test_ttx_family_naming_recommendation(self):
        "The font follows the font family naming recommendation."
        # See http://forum.fontlab.com/index.php?topic=313.0
        font = Font.get_ttfont(self.operator.path)

        # <Full name> limitation is < 64 chars
        length = len(Font.bin2unistring(font['name'].getName(4, 1, 0, 0)))
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        length = len(Font.bin2unistring(font['name'].getName(4, 3, 1, 1033)))
        self.assertLess(length, 64,
                        msg=('`Full Font Name` limitation is less'
                             ' than 64 chars. Now: %s') % length)

        # <Postscript name> limitation is < 30 chars
        length = len(Font.bin2unistring(font['name'].getName(6, 1, 0, 0)))
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        length = len(Font.bin2unistring(font['name'].getName(6, 3, 1, 1033)))
        self.assertLess(length, 30,
                        msg=('`PostScript Name` limitation is less'
                             ' than 30 chars. Now: %s') % length)

        # <Postscript name> may contain only a-zA-Z0-9
        # and one hyphen
        name = Font.bin2unistring(font['name'].getName(6, 1, 0, 0))
        self.assertRegexpMatches(name, r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(name.count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        name = Font.bin2unistring(font['name'].getName(6, 3, 1, 1033))
        self.assertRegexpMatches(name, r'[a-zA-Z0-9-]+',
                                 msg=('`PostScript Name` may contain'
                                      ' only a-zA-Z0-9 characters and'
                                      ' one hyphen'))
        self.assertLessEqual(name.count('-'), 1,
                             msg=('`PostScript Name` may contain only'
                                  ' one hyphen'))

        # <Family Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(1, 1, 0, 0)))
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        length = len(Font.bin2unistring(font['name'].getName(1, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <Style Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(2, 1, 0, 0)))
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        length = len(Font.bin2unistring(font['name'].getName(2, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Family Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(16, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Family Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        # <OT Style Name> limitation is 32 chars
        length = len(Font.bin2unistring(font['name'].getName(17, 3, 1, 1033)))
        self.assertLess(length, 32,
                        msg=('`OT Style Name` limitation is < 32 chars.'
                             ' Now: %s') % length)

        if 'OS/2' in font:
            # <Weight> value >= 250 and <= 900 in steps of 50
            self.assertTrue(bool(font['OS/2'].usWeightClass % 50 == 0),
                            msg=('OS/2 usWeightClass has to be in steps of 50.'
                                 ' Now: %s') % font['OS/2'].usWeightClass)

            self.assertGreaterEqual(font['OS/2'].usWeightClass, 250)
            self.assertLessEqual(font['OS/2'].usWeightClass, 900)

        if 'CFF' in font:
            self.assertTrue(bool(font['CFF'].Weight % 50 == 0),
                            msg=('CFF Weight has to be in steps of 50.'
                                 ' Now: %s') % font['CFF'].Weight)

            self.assertGreaterEqual(font['CFF'].Weight, 250)
            self.assertLessEqual(font['CFF'].Weight, 900)

    def test_glyphname_does_not_contain_disallowed_chars(self):
        """ GlyphName length < 30 and does contain allowed chars only """
        font = Font.get_ttfont(self.operator.path)

        for _, glyphName in enumerate(font.ttfont.getGlyphOrder()):
            if glyphName == '.notdef':
                continue
            if not re.match(r'(?![.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyphName):
                self.fail(('Glyph "%s" does not comply conventions.'
                           ' A glyph name may be up to 31 characters in length,'
                           ' must be entirely comprised of characters from'
                           ' the following set:'
                           ' A-Z a-z 0-9 .(period) _(underscore). and must not'
                           ' start with a digit or period. The only exception'
                           ' is the special character ".notdef". "twocents",'
                           ' "a1", and "_" are valid glyph names. "2cents"'
                           ' and ".twocents" are not.') % glyphName)

    def test_ttx_duplicate_glyphs(self):
        """ Font contains unique glyph names? """
        # (Duplicate glyph names prevent font installation on Mac OS X.)
        font = Font.get_ttfont(self.operator.path)
        glyphs = []
        for _, g in enumerate(font.ttfont.getGlyphOrder()):
            self.assertFalse(re.search(r'#\w+$', g),
                             msg="Font contains incorrectly named glyph %s" % g)
            glyphID = re.sub(r'#\w+', '', g)

            # Each GlyphID has to be unique in TTX
            self.assertFalse(glyphID in glyphs,
                             msg="GlyphID %s occurs twice in TTX" % g)
            glyphs.append(glyphs)

    def test_epar_in_keys(self):
        """ EPAR table present in font? """
        font = Font.get_ttfont(self.operator.path)
        self.assertIn('EPAR', font.ttfont.keys(), 'No')
