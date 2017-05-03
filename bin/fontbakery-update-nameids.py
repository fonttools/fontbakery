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
from fontTools.ttLib import TTFont
import argparse
from argparse import RawTextHelpFormatter

description = """

fontbakery-update-nameids.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update specific nameIDs in a collection of fonts with new strings.

Examples:

$ fontbakery-update-nameids.py -c="Copyright 2016" font.ttf
$ fontbakery-update-nameids.py -v="4.000" -ul="http://license.org" [fonts.ttf]

if you need to change the name or style of a collection of font families, use
fontbakery-nametable-from-filename.py instead.
"""


NAME_IDS = {
  0: 'copyright',
  3: 'uniqueid',
  5: 'version',
  7: 'trademark',
  8: 'manufacturer',
  9: 'designer',
  11: 'urlvendor',
  12: 'urldesigner',
  13: 'license',
  14: 'urllicense',
}

def swap_name(field, font_name_field, new_name):
  '''Replace a font's name field with a new name'''
  enc = font_name_field.getName(*field).getEncoding()
  text = str(font_name_field.getName(*field)).decode(enc)
  text = new_name
  font_name_field.setName(text, *field)


def update_field(arg, args, fields, nametable):
  if hasattr(args, arg):
    text = getattr(args, arg)
    if text:
      swap_name(fields, nametable, text)



parser = argparse.ArgumentParser(description=description,
                 formatter_class=RawTextHelpFormatter)
parser.add_argument('fonts', nargs="+")
parser.add_argument('-c', '--copyright', type=str,
                    help='Update copyright string')
parser.add_argument('-u', '--uniqueid', type=str,
                    help='Update uniqueid string')
parser.add_argument('-v', '--version', type=str,
                    help='Update version string')
parser.add_argument('-t', '--trademark', type=str,
                    help='Update trademark string')
parser.add_argument('-m', '--manufacturer', type=str,
                    help='Update manufacturer string')
parser.add_argument('-d', '--designer', type=str,
                    help='Update designer string')
parser.add_argument('-l', '--license', type=str,
                    help='Update license string')

parser.add_argument('-uv', '--urlvendor', type=str,
                    help='Update url vendor string')
parser.add_argument('-ud', '--urldesigner', type=str,
                    help='Update url vendor string')
parser.add_argument('-ul', '--urllicense', type=str,
                    help='Update url license string')


def main():
  args = parser.parse_args()

  for font_path in args.fonts:
    font = TTFont(font_path)
    for field in font['name'].names:
      fields = (field.nameID, field.platformID, field.platEncID, field.langID)
      if field.nameID in NAME_IDS:
        update_field(NAME_IDS[field.nameID], args, fields, font['name'])

    font.save(font_path + '.fix')
    print 'font saved %s.fix' % font_path


if __name__ == '__main__':
  main()
