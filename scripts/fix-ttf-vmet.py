#!/usr/bin/python
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

import os, sys
import argparse
from fontTools import ttLib

def get_bounds(font):
    ymin = 0
    ymax = 0
    # .OTF fonts do not contain a `glyf` table, 
    # but have a precomputed value in the `head` table
    if font.sfntVersion == 'OTTO':
        if hasattr(font['head'], 'yMin'):
            ymin = font['head'].yMin
        if hasattr(font['head'], 'yMax'):
            ymax = font['head'].yMax
    else:
        for g in font['glyf'].glyphs:
            char = font['glyf'][g]
            if hasattr(char, 'yMin') and ymin > char.yMin:
                ymin = char.yMin
                # print 'ymin is now ' + str(ymin)
            if hasattr(char, 'yMax') and ymax < char.yMax:
                ymax = char.yMax
                # print 'ymax is now ' + str(ymax)
    if ymin != 0 and ymax != 0:
        return(ymin, ymax)
    else:
        sys.exit("Unable to detect y values")

def show_metrics(font):
    ymin, ymax = get_bounds(font)
    print("ymax  is: {}".format(ymax))
    print("hhea asc: {}".format(font['hhea'].ascent))
    print("OS/2 asc: {}".format(font['OS/2'].sTypoAscender))
    print("Win  asc: {}".format(font['OS/2'].usWinAscent))
    print("ymin  is: {}".format(ymin))
    print("hhea des: {}".format(font['hhea'].descent))
    print("OS/2 des: {}".format(font['OS/2'].sTypoDescender))
    print("Win  des: {}".format(font['OS/2'].usWinDescent))
    print("hhea lng: {}".format(font['hhea'].lineGap))
    print("OS/2 lng: {}".format(font['OS/2'].sTypoLineGap))

def set_metrics(font, filename, ascents, descents, linegaps):
    font['hhea'].ascent = ascents
    font['OS/2'].sTypoAscender = ascents
    font['OS/2'].usWinAscent = ascents
    font['hhea'].descent = descents
    font['OS/2'].sTypoDescender = descents
    font['OS/2'].usWinDescent = abs(descents)
    font['hhea'].lineGap = linegaps
    font['OS/2'].sTypoLineGap = linegaps
    font.save(filename + '.fix')

def fix_metrics(font, filename):
    ymin, ymax = get_bounds(font)
    set_metrics(font, filename, ymax, ymin, 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascents', type=int, help="Set new ascents value in 'Horizontal Header' table ('hhea')")
    parser.add_argument('-d', '--descents', type=int, help="Set new descents value in 'Horizontal Header' table ('hhea')")
    parser.add_argument('-l', '--linegaps', type=int, help="Set new linegaps value in 'Horizontal Header' table ('hhea')")
    parser.add_argument('--autofix', action="store_true", help="Autofix font metrics")
    parser.add_argument('filename', help="Font file in OpenType (TTF/OTF) format")

    args = parser.parse_args()
    assert os.path.exists(args.filename)
    font = ttLib.TTFont(args.filename)
    if args.ascents and args.descents and args.linegaps:
        set_metrics(font, args.filename, args.ascents, args.descents, args.linegaps)
    elif args.autofix:
        fix_metrics(font, args.filename)
    else:
        show_metrics(font)

# check that all 3 args needed to set are needed for set to happen