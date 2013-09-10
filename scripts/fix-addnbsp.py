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
"""fixufo-addnbsp.py ensures nbspace glyph equals the space glyph.

Example:
$ fix-addnbsp.py Font-Regular.ufo;

$ fix-addnbsp.py Font-Regular.ufo Font-Regular-fixed.ufo;
"""
import sys
import os

def checkSpaces():
    if font[0x00a0].width == font['space'].width:
        print('nbspace width matches space width.')
        return True

if len(sys.argv) < 2:
    print __doc__
    sys.exit()

# Open the font
ufoFile = sys.argv[1]
# print('Starting FontForge: ')
import fontforge
try:
    # print('Opening ' + ufoFile),
    font = fontforge.open(ufoFile)
    # print('done.')
except:
    raise

# Determine if nbspace exists
nbspaceExists = False
for glyph in font.glyphs():
    if glyph.unicode == 0x00a0:
        nbspaceExists = True

# Determine if we need to do anything
if nbspaceExists:
    if checkSpaces():
        sys.exit()
# Do it
else:
    print('Copying space width to nbsppace,'),
    font.createMappedChar('nbspace')
    font[0x00a0].glyphname = 'nbspace'
    font.selection.select('space')
    font.copy()
    font.selection.select('nbspace')
    font.paste()
    print('done.')
    checkSpaces()

# Save the font
if len(sys.argv) == 3:
    ufoFileOut = sys.argv[2]
else: 
    ufoFileOut = sys.argv[1]
ufo = font.generate(ufoFileOut)
