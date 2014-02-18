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

import os
from fontTools import ttLib


def writeFont(font, filename):
    font.save(filename)
    print "Wrote font to", filename


def set_metrics(filename, ascents, descents, linegaps):
    font = ttLib.TTFont(filename)
    font['hhea'].ascent = ascents
    font['OS/2'].sTypoAscender = ascents
    font['OS/2'].usWinAscent = ascents
    font['hhea'].descent = descents
    font['OS/2'].sTypoDescender = descents
    font['OS/2'].usWinDescent = descents
    font['hhea'].lineGap = linegaps
    font['OS/2'].sTypoLineGap = linegaps
    writeFont(font, filename)


def fix_metrics(filename):
    font = ttLib.TTFont(filename)
    ymin = 0
    ymax = 0
    for g in font['glyf'].glyphs:
        char = font['glyf'][g]
        if hasattr(char, 'yMin') and ymin > char.yMin:
            ymin = char.yMin
        if hasattr(char, 'yMax') and ymax < char.yMax:
            ymax = char.yMax

    set_metrics(filename, ymax, ymin, 0)


def show_metrics(filename):
    font = ttLib.TTFont(filename)
    print("hhea asc:" + font['hhea'].ascent)
    print("OS/2 asc:" + font['OS/2'].sTypoAscender)
    print("OS/2 asc:" + font['OS/2'].usWinAscent)
    print("hhea des:" + font['hhea'].descent)
    print("OS/2 des:" + font['OS/2'].sTypoDescender)
    print("OS/2 des:" + font['OS/2'].usWinDescent)
    print("hhea lng:" + font['hhea'].lineGap)
    print("OS/2 lng:" + font['OS/2'].sTypoLineGap)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascents', type=int, help="Set new ascents value in 'Horizontal Header' table ('hhea')")
    parser.add_argument('-d', '--descents', type=int, help="Set new descents value in 'Horizontal Header' table ('hhea')")
    parser.add_argument('-l', '--linegaps', type=int, help="Set new linegaps value in 'Horizontal Header' table ('hhea')")
    parser.add_argument('--autofix', action="store_true", help="Autofix font metrics, overite file")
    parser.add_argument('filename', help="Font file in TTF format")

    args = parser.parse_args()
    assert os.path.exists(args.filename)
    if any([args.ascents, args.descents, args.linegaps]):
        set_metrics(args.filename, args.ascents, args.descents, args.linegaps)
    elif args.autofix:
        fix_metrics(args.filename)
    else:
        show_metrics(args.filename)
