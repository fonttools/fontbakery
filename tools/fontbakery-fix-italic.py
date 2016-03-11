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
from bakery_cli.nameid_values import *

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


class FixNotApplied(Exception):

    def __init__(self, message):
        self.message = message


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
            result_namerec.string = (val or '').encode(result_namerec.getEncoding())
    if result_namerec:
        return

    ot_namerecord = NameRecord()
    ot_namerecord.nameID = nameId
    ot_namerecord.platformID = 3
    ot_namerecord.langID = 0x409
    # When building a Unicode font for Windows, the platform ID
    # should be 3 and the encoding ID should be 1
    ot_namerecord.platEncID = 1
    ot_namerecord.string = (val or '').encode(ot_namerecord.getEncoding())

    font['name'].names.append(ot_namerecord)
    return


def setValidNames(font, isBold):
    name = font['name'].getName(1, 3, 1)
    familyname = name.string.decode(name.getEncoding())

    rules = NameTableNamingRule({'isBold': isBold,
                                 'isItalic': True,
                                 'familyName': familyname,
                                 'weight': font['OS/2'].usWeightClass})

    names = []
    passedNamesId = []

    for rec in font['name'].names:
        string = rec.string.decode(rec.getEncoding())
            
        if rec.nameID in [NAMEID_FONT_FAMILY_NAME,\
                          NAMEID_FONT_SUBFAMILY_NAME,\
                          NAMEID_FULL_FONT_NAME,\
                          NAMEID_POSTSCRIPT_NAME,\
                          NAMEID_TYPOGRAPHIC_FAMILY_NAME,\
                          NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME,\
                          NAMEID_COMPATIBLE_FULL_MACONLY]:
            string = rules.apply(rec.nameID)
            passedNamesId.append(rec.nameID)
        names.append({'nameID': rec.nameID, 'string': string})

    difference = set([NAMEID_FONT_FAMILY_NAME,\
                      NAMEID_FONT_SUBFAMILY_NAME,\
                      NAMEID_FULL_FONT_NAME,\
                      NAMEID_POSTSCRIPT_NAME,\
                      NAMEID_TYPOGRAPHIC_FAMILY_NAME,\
                      NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME,\
                      NAMEID_COMPATIBLE_FULL_MACONLY]).difference(set(passedNamesId))
    if difference:
        for nameID in difference:
            string = rules.apply(nameID)
            names.append({'nameID': nameID, 'string': string})

    for field in names:
        setValidNameRecord(font, field['nameID'], field['string'])

    for name in font['name'].names:
        logger.debug(u'{}: {}'.format(name.nameID, name.string.decode(name.getEncoding())))


def italicAngle(font, newvalue):
    font['post'].italicAngle = newvalue


def getSuggestedItalicAngle(font):
    return -10


def validate(font, fontStyle):
    errors = []

    f = '{:#09b}'.format(font['head'].macStyle)

    if fontStyle.endswith('Italic'):
        if not fontStyleIsBold(fontStyle):
            if not bool(font['head'].macStyle & 0b10):
                errors.append(('ER: HEAD macStyle is {} should be 00000010'.format(f),
                               setMacStyle, [font, font['head'].macStyle | 0b10]))
        elif not bool(font['head'].macStyle & 0b11):
            errors.append(('ER: HEAD macStyle is {} should be 00000011'.format(f),
                           setMacStyle, [font, font['head'].macStyle | 0b11]))
    else:
        if not fontStyleIsBold(fontStyle):
            if bool(font['head'].macStyle & 0b10):
                newvalue = font['head'].macStyle | 0b1111111111111100
                errors.append(('ER: HEAD macStyle is {} should be {:#09b}'.format(f, newvalue),
                               setMacStyle, [font, newvalue]))
        elif bool(font['head'].macStyle & 0b01):
            newvalue = font['head'].macStyle | 0b1111111111111101
            errors.append(('ER: HEAD macStyle is {} should be {:#09b}'.format(f, newvalue),
                           setMacStyle, [font, newvalue]))

    if font['post'].italicAngle != 0 and not fontStyle.endswith('Italic'):
        errors.append(('ER: POST italicAngle is {} should be 0'.format(font['post'].italicAngle),
                       italicAngle, [font, 0]))

    if font['post'].italicAngle == 0 and fontStyle.endswith('Italic'):
        newvalue = getSuggestedItalicAngle(font)
        errors.append(('ER: POST italicAngle is 0 should be {}'.format(newvalue),
                       italicAngle, [font, newvalue]))

    # Check NAME table contains correct names for Italic
    if fontStyle.endswith('Italic'):

        if not fontStyleIsBold(fontStyle):
            if font['OS/2'].fsSelection & 0b000001:
                logger.info('OK: OS/2 fsSelection')
            else:
                newvalue = font['OS/2'].fsSelection | 0b1
                msg = 'ER: OS/2 fsSelection is {:#06b} should be {:#06b}'
                errors.append((msg.format(font['OS/2'].fsSelection, newvalue),
                               setFsSelection, [font, newvalue]))
        else:
            if font['OS/2'].fsSelection & 0b100001:
                logger.info('OK: OS/2 fsSelection')
            else:
                newvalue = font['OS/2'].fsSelection | 0b100001
                msg = 'ER: OS/2 fsSelection is {:#06b} should be {:#06b}'
                errors.append((msg.format(font['OS/2'].fsSelection, newvalue),
                               setFsSelection, [font, newvalue]))

    elif fontStyleIsBold(fontStyle):
        if font['OS/2'].fsSelection & 0b100000:
            logger.info('OK: OS/2 fsSelection')
        else:
            newvalue = font['OS/2'].fsSelection | 0b100000
            msg = 'ER: OS/2 fsSelection is {:#06b} should be {:#06b}'
            errors.append((msg.format(font['OS/2'].fsSelection, newvalue),
                           setFsSelection, [font, newvalue]))

    for name in font['name'].names:
        if name.nameID not in [NAMEID_FONT_SUBFAMILY_NAME,\
                               NAMEID_FULL_FONT_NAME,\
                               NAMEID_POSTSCRIPT_NAME,\
                               NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME]:
            continue

        string = name.string.decode(name.getEncoding())

        if fontStyle.endswith('Italic'):
            if string.endswith('Italic'):
                logger.info('OK: NAME ID{}:\t{}'.format(name.nameID, string))
            else:
                errors.append(('ER: NAME ID{}:\t{}'.format(name.nameID, string),
                               setValidNames, [font, fontStyleIsBold(fontStyle)]))
        elif fontStyleIsBold(fontStyle):
            if fontStyleIsBold(string):
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

    fontStyle = name.string.decode(name.getEncoding())

    errors = validate(font, fontStyle)
    if errors:
        for error, function, arguments in errors:
            logger.error(error)
            if args.autofix and function:
                try:
                    function(*arguments)
                except FixNotApplied as ex:
                    logger.error('ER: Fix can not be applied. See details below')
                    logger.error('\t{}'.format(ex.message))
                    continue
        font.save(path + '.fix')

