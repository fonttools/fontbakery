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
#
# Based on http://typophile.com/node/13081
# Also see http://typophile.com/node/13081
import argparse
import os
import sys
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


def get_metrics(ttfont):
    ymin, ymax = get_bounds(ttfont)
    return {
        'ymax': ymax,
        'ymin': ymin,
        'hhea_ascent': ttfont['hhea'].ascent,
        'hhea_descent': ttfont['hhea'].descent,
        'OS2_sTypeAscender': ttfont['OS/2'].sTypoAscender,
        'OS2_sTypeDescender': ttfont['OS/2'].sTypoDescender,
        'OS2_usWinAscent': ttfont['OS/2'].usWinAscent,
        'OS2_usWinDescent': ttfont['OS/2'].usWinDescent,
        'lineGap': ttfont['hhea'].lineGap,
        'OS2_lineGap': ttfont['OS/2'].sTypoLineGap
    }


class VmetFix:

    def __init__(self, fonts):
        self.fonts = fonts

    def set_metrics_for_font(self, ttfont, ascents, descents, linegaps):
        ttfont['hhea'].ascent = ascents
        ttfont['OS/2'].sTypoAscender = ascents
        ttfont['OS/2'].usWinAscent = ascents
        ttfont['hhea'].descent = descents
        ttfont['OS/2'].sTypoDescender = descents
        ttfont['OS/2'].usWinDescent = abs(descents)
        ttfont['hhea'].lineGap = linegaps
        ttfont['OS/2'].sTypoLineGap = linegaps

    def set_metrics(self, ascents, descents, linegaps):
        for fontpath in self.fonts:
            ttfont = ttLib.TTFont(fontpath)
            self.set_metrics_for_font(ttfont, ascents, descents, linegaps)
            ttfont.save(fontpath + '.fix')

    def fix_metrics(self):
        for fontpath in self.fonts:
            ttfont = ttLib.TTFont(fontpath)
            ymin, ymax = get_bounds(ttfont)
            self.set_metrics_for_font(ttfont, ymax, ymin, 0)
            ttfont.save(fontpath + '.fix')

    def show_metrics(self):
        fonts = []
        for fontpath in self.fonts:
            ttfont = ttLib.TTFont(fontpath)
            metrics = get_metrics(ttfont)
            metrics.update({'name': os.path.basename(fontpath)})
            fonts.append(metrics)

        def row(key, title=None):
            return [title or key] + map(lambda x: x[key], fonts)

        header = ['Parameter'] + map(lambda x: x['name'], fonts)
        formatstring = ('{:<%s}' * (len(fonts) + 1))
        formatstring = formatstring % tuple(map(lambda x: len(x) + 4, header))
        print(formatstring.format(*header))
        print(formatstring.format(*row('ymax')))
        print(formatstring.format(*row('hhea_ascent', 'hhea asc')))
        print(formatstring.format(*row('OS2_sTypeAscender', 'OS/2 asc')))
        print(formatstring.format(*row('OS2_usWinAscent', 'Win asc')))

        print(formatstring.format(*row('ymin')))
        print(formatstring.format(*row('hhea_descent', 'hhea desc')))
        print(formatstring.format(*row('OS2_sTypeDescender', 'OS/2 desc')))
        print(formatstring.format(*row('OS2_usWinDescent', 'Win desc')))
        print(formatstring.format(*row('lineGap', 'hhea lng')))
        print(formatstring.format(*row('OS2_lineGap', 'OS/2 lng')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascents', type=int,
                        help=("Set new ascents value in 'Horizontal Header'"
                              " table ('hhea')"))
    parser.add_argument('-d', '--descents', type=int,
                        help=("Set new descents value in 'Horizontal Header'"
                              " table ('hhea')"))
    parser.add_argument('-l', '--linegaps', type=int,
                        help=("Set new linegaps value in 'Horizontal Header'"
                              " table ('hhea')"))
    parser.add_argument('--autofix', action="store_true",
                        help="Autofix font metrics")
    parser.add_argument('filename', nargs='+',
                        help="Font file in OpenType (TTF/OTF) format")

    args = parser.parse_args()
    vmetfixer = VmetFix(args.filename)
    if args.ascents and args.descents and args.linegaps:
        vmetfixer.set_metrics(args.ascents, args.descents, args.linegaps)
    elif args.autofix:
        vmetfixer.fix_metrics()
    else:
        vmetfixer.show_metrics()
