#!/usr/bin/python
#
# Copyright 2010, Google Inc.
# Author: Dave Crossland (dave@understandinglimited.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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

fontbakery-update-version.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update a collection of fonts version number to a new version number.

e.g:
python fontbakery-update-version.py [fonts] 2.300 2.301

"""

parser = argparse.ArgumentParser(description=description,
                                 formatter_class=RawTextHelpFormatter)
parser.add_argument('fonts',
          nargs="+",
          help="Fonts in OpenType (TTF/OTF) format")
parser.add_argument('old_version',
          help="Old version number",
          type=str)
parser.add_argument('new_version',
          help="New Version number",
          type=str)


def main():
  args = parser.parse_args()
  for font_path in args.fonts:
    font = TTFont(font_path)

    v_updated = False
    for field in font['name'].names:
      enc = field.getEncoding()
      field_text = str(field).decode(enc)
      if args.old_version in field_text:
        updated_text = field_text.replace(
          args.old_version,
          args.new_version
        )
        font['name'].setName(
          updated_text,
          field.nameID,
          field.platformID,
          field.platEncID,
          field.langID
        )
        v_updated = True
    if v_updated:
      font['head'].fontRevision = float(args.new_version)
      print '%s version updated from %s to %s' % (
        font_path,
        args.old_version,
        args.new_version
      )
      font.save(font_path + '.fix')
      print 'font saved %s.fix' % font_path
    else:
      print '%s skipping. Could not find old version number %s' % (
        font_path,
        args.old_version
      )


if __name__ == '__main__':
  main()
