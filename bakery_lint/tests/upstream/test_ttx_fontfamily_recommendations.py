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
from fontTools.ttLib import TTFont

from bakery_lint.base import BakeryTestCase as TestCase


def bin2unistring(record):
    if not record:
        return ''

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
    name = __name__
    tool = 'TTFont'

    def test_ttx_family_naming_recommendation(self):
        """ The font corresponds the font family naming recommendation.
        See http://forum.fontlab.com/index.php?topic=313.0 """
        if not self.operator.path.lower().endswith('.ttx'):
            return
        font = TTFont(None)
        font.importXML(self.operator.path, quiet=True)

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
