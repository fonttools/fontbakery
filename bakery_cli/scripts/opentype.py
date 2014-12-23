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
from bakery_cli.ttfont import Font, getSuggestedFontNameValues
from fontTools.ttLib.tables._n_a_m_e import NameRecord


def findOrCreateNameRecord(nametable, nameId, platformId=3, langId=0x409, platEncId=1):
    result_namerec = nametable.getName(nameId, platformId, platEncId)
    if result_namerec:
        return result_namerec

    ot_namerecord = NameRecord()
    ot_namerecord.nameID = nameId
    ot_namerecord.platformID = platformId
    ot_namerecord.langID = langId

    # When building a Unicode font for Windows, the platform ID
    # should be 3 and the encoding ID should be 1
    ot_namerecord.platEncID = platEncId

    nametable.names.append(ot_namerecord)
    return ot_namerecord


mapping = {
    'Thin': 'Regular',
    'Extra Light': 'Regular',
    'Light': 'Regular',
    'Regular': 'Regular',
    'Medium': 'Regular',
    'SemiBold': 'Regular',
    'Extra Bold': 'Regular',
    'Black': 'Regular',

    'Thin Italic': 'Italic',
    'Extra Light Italic': 'Italic',
    'Light Italic': 'Italic',
    'Italic': 'Italic',
    'Medium Italic': 'Italic',
    'SemiBold Italic': 'Italic',
    'Extra Bold Italic': 'Italic',
    'Black Italic': 'Bold Italic',

    'Bold': 'Bold',
    'Bold Italic': 'Bold Italic'
}


def fix(fontpath):
    ttfont = Font.get_ttfont(fontpath)

    values = getSuggestedFontNameValues(ttfont.ttfont)

    family_name = values['family']

    subfamily_name = values['subfamily']

    for pair in [[4, 3, 1], [4, 1, 0]]:
        name = ttfont.ttfont['name'].getName(*pair)
        if name:
            name.string = ' '.join([family_name.replace(' ', ''), subfamily_name]).encode('utf_16_be')

    for pair in [[6, 3, 1], [6, 1, 0]]:
        name = ttfont.ttfont['name'].getName(*pair)
        if name:
            name.string = '-'.join([family_name.replace(' ', ''), subfamily_name.replace(' ', '')]).encode('utf_16_be')

    for pair in [[1, 3, 1], [1, 1, 0]]:
        name = ttfont.ttfont['name'].getName(*pair)
        if name:
            name.string = family_name.replace(' ', '').encode('utf_16_be')

    for pair in [[2, 3, 1], [2, 1, 0]]:
        name = ttfont.ttfont['name'].getName(*pair)
        if name:
            name.string = subfamily_name.encode('utf_16_be')

    ot_namerecord = findOrCreateNameRecord(ttfont['name'], 16)
    ot_namerecord.string = family_name.replace(' ', '').encode("utf_16_be")

    ot_namerecord = findOrCreateNameRecord(ttfont['name'], 17)
    ot_namerecord.string = mapping.get(subfamily_name, 'Regular').encode("utf_16_be")

    ot_namerecord = findOrCreateNameRecord(ttfont['name'], 18)
    ot_namerecord.string = ' '.join([family_name.replace(' ', ''), mapping.get(subfamily_name, 'Regular')]).encode("utf_16_be")

    ttfont.save(fontpath + '.fix')
