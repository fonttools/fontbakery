#!/usr/bin/env python
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
from __future__ import print_function
import argparse
import logging
import os

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from bakery_cli.logger import logger
from bakery_cli.utils import NameTableNamingRule


description = ''

parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font', nargs='+',
                    help="Font in OpenType (TTF/OTF) format")
parser.add_argument('--autofix', action="store_true",
                    help="Autofix font metrics")
parser.add_argument('--verbose', action='store_true',
                    help='Print output in verbose')

args = parser.parse_args()


if args.verbose:
    logger.setLevel(logging.DEBUG)


def fontStyleIsBold(fontStyle):
    try:
        fontStyle.index('Bold')
    except ValueError:
        return False
    return True


def setMacStyle(font, newvalue):
    font['head'].macStyle = newvalue


def setFsSelection(font, newvalue):
    font['OS/2'].fsSelection = newvalue


def setValidNameRecord(font, nameId, val):
    result_namerec = None
    for k, p in [[1, 0], [3, 1]]:
        result_namerec = font['name'].getName(nameId, k, p)
        if result_namerec:
            if result_namerec.isUnicode():
                result_namerec.string = (val or '').encode("utf-16-be")
            else:
                result_namerec.string = val or ''
    if result_namerec:
        return

    ot_namerecord = NameRecord()
    ot_namerecord.nameID = nameId
    ot_namerecord.platformID = 3
    ot_namerecord.langID = 0x409
    # When building a Unicode font for Windows, the platform ID
    # should be 3 and the encoding ID should be 1
    ot_namerecord.platEncID = 1
    if ot_namerecord.isUnicode():
        ot_namerecord.string = (val or '').encode("utf-16-be")
    else:
        ot_namerecord.string = val or ''

    font['name'].names.append(ot_namerecord)
    return


def setValidNames(font, isBold):
    name = font['name'].getName(1, 3, 1)
    familyname = name.string
    if name.isUnicode():
        familyname = familyname.decode('utf-16-be')

    rules = NameTableNamingRule({'isBold': isBold,
                                 'isItalic': True,
                                 'familyName': familyname,
                                 'weight': font['OS/2'].usWeightClass})

    names = []
    passedNamesId = []

    for rec in font['name'].names:
        string = rec.string
        if rec.isUnicode():
            string = string.decode('utf-16-be')
        if rec.nameID in [1, 2, 4, 6, 16, 17, 18]:
            string = rules.apply(rec.nameID)
            passedNamesId.append(rec.nameID)
        names.append({'nameID': rec.nameID, 'string': string})

    difference = set([1, 2, 4, 6, 16, 17, 18]).difference(set(passedNamesId))
    if difference:
        for nameID in difference:
            string = rules.apply(nameID)
            names.append({'nameID': nameID, 'string': string})
            
    for field in names:
        setValidNameRecord(font, field['nameID'], field['string'])

    for name in font['name'].names:
        if name.isUnicode():
            logger.debug(u'{}: {}'.format(name.nameID, name.string.decode('utf-16-be')))
        else:
            logger.debug(u'{}: {}'.format(name.nameID, name.string))


def validate(font, fontStyle):
    errors = []

    f = '{:#010b}'.format(font['head'].macStyle)
    if not fontStyleIsBold(fontStyle):
        if not bool(font['head'].macStyle & 0b10):
            errors.append(('ER: HEAD macStyle is {} should be 00000010'.format(f), 
                           setMacStyle, [font, font['head'].macStyle | 0b10]))
    elif not bool(font['head'].macStyle & 0b11):
        errors.append(('ER: HEAD macStyle is {} should be 00000011'.format(f), 
                       setMacStyle, [font, font['head'].macStyle | 0b11]))

    if font['post'].italicAngle == 0:
        errors.append(('ER: POST italicAngle is 0 should be -13', None, []))

    # Check NAME table contains correct names for Italic
    if font['OS/2'].fsSelection & 0b1:
        logger.info('OK: OS/2 fsSelection')
    else:
        errors.append(('ER: OS/2 fsSelection',
                       setFsSelection, [font, font['OS/2'].fsSelection | 0b1]))

    for name in font['name'].names:
        if name.nameID not in [2, 4, 6, 17]:
            continue

        string = name.string
        if name.isUnicode():
            string = string.decode('utf-16-be')

        if string.endswith('Italic'):
            logger.info('OK: NAME ID{}:\t{}'.format(name.nameID, string))
        else:
            errors.append(('ER: NAME ID{}:\t{}'.format(name.nameID, string),
                           setValidNames, [font, fontStyleIsBold(fontStyle)]))

    return errors


for path in args.ttf_font:

    if not os.path.exists(path):
        continue

    font = TTFont(path)

    name = font['name'].getName(2, 3, 1)
    if not name:
        continue

    fontStyle = name.string
    if name.isUnicode():
        fontStyle = fontStyle.decode('utf-16-be')

    if not fontStyle.endswith('Italic'):
      logger.info('OK: {}'.format(path))
      continue

    errors = validate(font, fontStyle)
    if errors:
        for error, function, arguments in errors:
            logger.error(error)
            if args.autofix and function:
                function(*arguments)
                font.save(path + '.fix')

