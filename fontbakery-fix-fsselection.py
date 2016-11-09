#!/usr/bin/env python
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
import csv
import os
import sys

from fontTools import ttLib
import tabulate

parser = argparse.ArgumentParser(description='Print out fsSelection'
                                             ' bitmask of the fonts')
parser.add_argument('font', nargs="+")
parser.add_argument('--csv', default=False, action='store_true')
parser.add_argument('--autofix', default=False, action='store_true')

STYLE_NAMES = ["Thin",
               "ExtraLight",
               "Light",
               "Regular",
               "Medium",
               "SemiBold",
               "Bold",
               "ExtraBold",
               "Black",
               "Thin Italic",
               "ExtraLight Italic",
               "Light Italic",
               "Italic",
               "Medium Italic",
               "SemiBold Italic",
               "Bold Italic",
               "ExtraBold Italic",
               "Black Italic"]

RIBBI_STYLE_NAMES = ["Regular",
                     "Italic",
                     "Bold",
                     "BoldItalic"]


def getByte2(ttfont):
  return ttfont['OS/2'].fsSelection >> 8


def getByte1(ttfont):
  return ttfont['OS/2'].fsSelection & 255


def printInfo(fonts, print_csv=False):
  rows = []
  headers = ['filename', 'fsSelection']
  for font in fonts:
    ttfont = ttLib.TTFont(font)
    row = [os.path.basename(font)]
    row.append(('{:#010b} '
                '{:#010b}'
                '').format(getByte2(ttfont),
                           getByte1(ttfont)).replace('0b', ''))
    rows.append(row)

  def as_csv(rows):
    writer = csv.writer(sys.stdout)
    writer.writerows([headers])
    writer.writerows(rows)
    sys.exit(0)

  if print_csv:
    as_csv(rows)
  else:
    print(tabulate.tabulate(rows, headers, tablefmt="pipe"))

def _style(font):
  filename_base = font.split('.')[0]
  return filename_base.split('-')[-1]

def _familyname(font):
  filename_base = font.split('.')[0]
  names = filename_base.split('-')
  names.pop()
  return '-'.join(names)

def is_italic(font):
  return 'Italic' in _style(font)

def is_regular(font):
  style = _style(font)
  return ("Regular" in style or
          (style in STYLE_NAMES and
           style not in RIBBI_STYLE_NAMES and
           "Italic" not in style))

def is_bold(font):
  return _style(font) in ["Bold", "BoldItalic"]

def is_canonical(font):
  if '-' not in font:
    return False
  else:
    style = _style(font)
    for valid in STYLE_NAMES:
      valid = ''.join(valid.split(' '))
      if style == valid:
        return True
    # otherwise:
    return False

def main():
  args = parser.parse_args()
  if args.autofix:
    fixed_fonts = []
    for font in args.font:
      ttfont = ttLib.TTFont(font)

      if not is_canonical(font):
        print("Font filename is not canonical: '{}'".format(font))
        exit(-1)

      initial_value = ttfont['OS/2'].fsSelection

      if is_regular(font):
        ttfont['OS/2'].fsSelection |= 0b1000000
      else:
        ttfont['OS/2'].fsSelection &= ~0b1000000

      if is_bold(font):
        ttfont['OS/2'].fsSelection |= 0b100000
      else:
        ttfont['OS/2'].fsSelection &= ~0b100000

      if is_italic(font):
        ttfont['OS/2'].fsSelection |= 0b1
      else:
        ttfont['OS/2'].fsSelection &= ~0b1

      if ttfont['OS/2'].fsSelection != initial_value:
        fixed_fonts.append(font)
        ttfont.save(font + '.fix')


    if len(fixed_fonts) > 0:
      printInfo([f + '.fix' for f in fixed_fonts], print_csv=args.csv)

    sys.exit(0)

  printInfo(args.font, print_csv=args.csv)


if __name__ == '__main__':
    main()

