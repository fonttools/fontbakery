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

import copy

import fontTools.ttLib


def add_spua_by_glyph_id_mapping_to_cmap(ttx, fontpath, unencoded_glyphs):
    """ Add SPUA by Glyph ID to cmap.

    :param ttx: instance of `fontTools.ttLib.TTFont`.
    :param fontpath: The path to the font file we are reading data from.
    :param unencoded_glyphs: list of unencoded glyphs.
    :return: instance of `ttLib.TTFont` with modified 'cmap'.
    """

    if not unencoded_glyphs:
        return

    ucs2cmap = None
    cmap = ttx["cmap"]

    # Check if an UCS-2 cmap exists
    for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
        ucs2cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
        if ucs2cmap:
            break
    # Create UCS-4 cmap and copy the contents of UCS-2 cmap
    # unless UCS 4 cmap already exists
    ucs4cmap = cmap.getcmap(3, 10)
    if not ucs4cmap:
        cmapModule = fontTools.ttLib.getTableModule('cmap')
        ucs4cmap = cmapModule.cmap_format_12(12)
        ucs4cmap.platformID = 3
        ucs4cmap.platEncID = 10
        ucs4cmap.language = 0
        if ucs2cmap:
            ucs4cmap.cmap = copy.deepcopy(ucs2cmap.cmap)
        cmap.tables.append(ucs4cmap)
    # Map all glyphs to UCS-4 cmap Supplementary PUA-A codepoints
    # by 0xF0000 + glyphID
    ucs4cmap = cmap.getcmap(3, 10)
    for glyphID, glyphName in enumerate(ttx.getGlyphOrder()):
        if glyphName in unencoded_glyphs:
            ucs4cmap.cmap[0xF0000 + glyphID] = glyphName
    ttx['cmap'] = cmap
    ttx.save('{}.fix'.format(fontpath))
    ttx.close()
    return ttx


def get_unencoded_glyphs(ttx):
    """ Check if font has unencoded glyphs """
    cmap = ttx['cmap']

    new_cmap = cmap.getcmap(3, 10)
    if not new_cmap:
        for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
            new_cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
            if new_cmap:
                break

    assert new_cmap

    diff = list(set(ttx.glyphOrder) - set(new_cmap.cmap.values()) - {'.notdef'})
    return [g for g in diff[:] if g != '.notdef']
