#!/usr/bin/python
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
#
# bbox.py: A FontForge python script for printing bounding boxes
# to stdout in this format:
#
#   glyphname xmin ymin xmax ymax
#
# Usage:
#
#   $ python bbox.py Font.ttf 2> /dev/null
#   A 42.0 -32.0 782.0 1440.0
#   B 46.0 -72.0 752.0 1478.0
#   C 53.0 -26.0 821.0 1442.0
#   D 77.0 -26.0 773.0 1442.0

import argparse
import fontforge, sys
from fontTools.ttLib import TTFont

description = "A Python script for printing bounding boxes to stdout"
parser = argparse.ArgumentParser(description=description)
parser.add_argument('fonts',
                    nargs="+",
                    help="Fonts in OpenType (TTF/OTF) format")
group = parser.add_mutually_exclusive_group()
group.add_argument('--glyphs', default=False, action="store_true")
group.add_argument('--family', default=False, action="store_true",
                   help='Return the bounds for a family of fonts')


def main():
    args = parser.parse_args()

    for font in args.fonts:
        font_path = font
        if args.glyphs:
            font = fontforge.open(font)
            for g in fontforge.activeFont().glyphs():
                bbox = g.boundingBox()
                print font_path,
                print str(g.glyphname),
                print str(bbox[0]),
                print str(bbox[1]),
                print str(bbox[2]),
                print str(bbox[3])

        elif args.family:
            print font_path
            font = TTFont(font_path)
            print font_path,
            print font['head'].xMin,
            print font['head'].yMin,
            print font['head'].xMax,
            print font['head'].yMax


if __name__ == '__main__':
    main()
