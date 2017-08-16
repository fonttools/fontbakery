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
from os.path import basename
from argparse import ArgumentParser
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable


description = """

fontbakery-fix-cmap.py
~~~~~~~~~~~~~~~~~~~~~~

Manipulate a collection of fonts' cmap tables.
"""


def convert_cmap_subtables_to_v4(font):
  cmap = font['cmap']
  outtables = []
  for table in cmap.tables:
    newtable = CmapSubtable.newSubtable(4)
    newtable.platformID = table.platformID
    newtable.platEncID = table.platEncID
    newtable.language = table.language
    newtable.cmap = table.cmap
    outtables.append(newtable)
  font['cmap'].tables = outtables


def remove_cmap_subtable(font, plat_id, enc_id):
  for table in font['cmap'].tables:
    if table.platformID == plat_id and table.platEncID == enc_id:
      font['cmap'].tables.remove(table)


def main():
  parser = ArgumentParser(description=description)
  parser.add_argument('fonts', nargs='+')
  parser.add_argument('--format-4-subtables', '-f4', default=False,
                      action='store_true',
                      help="Convert cmap subtables to format 4")
  parser.add_argument('-drop-mac-subtable', '-dm', default=False,
                      action='store_true',
                      help='Drop Mac cmap subtables')
  args = parser.parse_args()

  for path in args.fonts:
    font = TTFont(path)
    font_filename = basename(path)
    fixit = False

    if args.format_4_subtables:
      print('%s: Converting Cmap subtables to format 4' % font_filename)
      convert_cmap_subtables_to_v4(font)
      fixit = True

    if args.drop_mac_subtable:
      if font['cmap'].getcmap(1, 0):
        print('%s: Dropping Cmap Mac subtable' % font_filename)
        remove_cmap_subtable(font, 1, 0)
        fixit = True

    if fixit:
      print('Saving %s to %s.fix' % (font_filename, path))
      font.save(path + '.fix')


if __name__ == '__main__':
  main()
