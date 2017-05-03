#!/usr/bin/env python
#
# Copyright 2010, Google Inc.
# Author: Dave Crossland (dave@understandinglimited.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
from argparse import RawTextHelpFormatter
import csv
import sys
from fontTools.ttLib import TTFont
import tabulate

description = """

fontbakery-check-bbox.py
~~~~~~~~~~~~~~~~~~~~~~~~

A Python script for printing bounding boxes to stdout.

Users can either check a collection of fonts bounding boxes (--family) or
the bounding box for each glyph in the collection of fonts (--glyphs).

Extremes coordinates for each category can be returned with the argument
--extremes.

e.g:

Check bounding boxes of fonts in collection:
python fontbakery-check-bbox.py --family [fonts]

Check bounding boxes of glyphs in fonts collection:
python fontbakery-check-bbox.py --glyphs [fonts]

Find the extreme coordinates for the bounding boxes in the fonts collection:
python fontbakery-check-bbox.py --family --extremes [fonts]

"""
parser = argparse.ArgumentParser(description=description,
                                 formatter_class=RawTextHelpFormatter)
parser.add_argument('fonts',
                    nargs="+",
                    help="Fonts in OpenType (TTF/OTF) format")
parser.add_argument('--csv', default=False, action='store_true')
parser.add_argument('--extremes', default=False, action='store_true')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--glyphs', default=False, action="store_true")
group.add_argument('--family', default=False, action="store_true",
                   help='Return the bounds for a family of fonts')


def printInfo(rows, save=False):
    header = [r[0] for r in rows[0]]
    t = []
    for row in rows:
        t.append([r[1] for r in row])

    if save:
        writer = csv.writer(sys.stdout)
        writer.writerows([header])
        writer.writerows(t)
        sys.exit(0)
    else:
        print(tabulate.tabulate(t, header, tablefmt="pipe"))


def find_extremes(rows):
    extremes = {}

    for row in rows:
        for k, v in row:
            if type(v) == str:
                continue
            if k not in extremes:
                extremes[k] = int(v)
            else:
                if abs(int(v)) > abs(extremes[k]):
                    extremes[k] = v
    return [extremes.items()]


def main():
    args = parser.parse_args()

    rows = []
    for font in args.fonts:
        font_path = font
        font = TTFont(font_path)
        if args.glyphs:
            for g_name in font['glyf'].glyphs:
                glyph = font['glyf'][g_name]
                try:
                    rows.append([
                        ("Font", font_path),
                        ("Glyph", g_name),
                        ("xMin", glyph.xMin),
                        ("yMin", glyph.yMin),
                        ("xMax", glyph.xMax),
                        ("yMax", glyph.yMax)
                    ])
                except AttributeError:
                    # glyphs without paths or components don't have
                    # yMin, yMax etc
                    rows.append([
                        ("Font", font_path),
                        ("Glyph", g_name),
                        ("xMin", 0),
                        ("yMin", 0),
                        ("xMax", 0),
                        ("yMax", 0)
                    ])
                    pass


        elif args.family:
            rows.append([
                ("Font", font_path),
                ("xMin", font['head'].xMin),
                ("yMin", font['head'].yMin),
                ("xMax", font['head'].xMax),
                ("yMax", font['head'].yMax)
            ])

    if args.extremes:
        rows = find_extremes(rows)

    if args.csv:
        printInfo(rows, save=True)
    else:
        printInfo(rows)

if __name__ == '__main__':
    main()
