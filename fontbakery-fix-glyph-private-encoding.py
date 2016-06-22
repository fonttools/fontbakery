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
import os

import fontTools.ttLib
from bakery_cli.fixers import AddSPUAByGlyphIDToCmap, get_unencoded_glyphs


description = 'Fixes TTF unencoded glyphs to have Private Use Area encodings'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font', nargs='+',
                    help='Font in OpenType (TTF/OTF) format')
parser.add_argument('--autofix', action="store_true",
                    help='Apply autofix. '
                         'Otherwise just check if there are unencoded glyphs')

def get_unencoded_glyphs(font):
    """ Check if font has unencoded glyphs """
    cmap = font['cmap']

    new_cmap = cmap.getcmap(3, 10)
    if not new_cmap:
        for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
            new_cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
            if new_cmap:
                break

    if not new_cmap:
        return []

    diff = list(set(font.getGlyphOrder()) - set(new_cmap.cmap.values()) - {'.notdef'})
    return [g for g in diff[:] if g != '.notdef']


class AddSPUAByGlyphIDToCmap(object):

    def __init__(self, path):
        self.font = ttLib.TTFont(path)
        self.path = path
        self.saveit = False

    def __del__(self):
       if self.saveit:
           self.font.save(self.path + ".fix")

    def fix(self):
        unencoded_glyphs = get_unencoded_glyphs(self.font)
        if not unencoded_glyphs:
            return

        ucs2cmap = None
        cmap = self.font["cmap"]

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
        for glyphID, glyph in enumerate(self.font.getGlyphOrder()):
            if glyph in unencoded_glyphs:
                ucs4cmap.cmap[0xF0000 + glyphID] = glyph
        self.font['cmap'] = cmap
        return True



args = parser.parse_args()

for path in args.ttf_font:
    if not os.path.exists(path):
        continue

    if args.autofix:
        AddSPUAByGlyphIDToCmap(path).fix()
    else:
        font = fontTools.ttLib.TTFont(path, 0)
        print("\nThese are the unencoded glyphs in font file '{0}':\n{1}".format(path, '\n'.join(get_unencoded_glyphs(font))))
