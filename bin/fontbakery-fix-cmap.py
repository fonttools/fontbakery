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


description = "Manipulate a collection of fonts' cmap tables."


def convert_cmap_subtables_to_v4(font):
  cmap = font['cmap']
  outtables = []
  fixit = False
  for table in cmap.tables:
    if table.format != 4:
      print(('Converted format {} cmap subtable'
             ' with Platform ID = {} and Encoding ID = {}'
             ' to format 4.').format(table.format,
                                     table.platformID,
                                     table.platEncID))
      fixit = True
    newtable = CmapSubtable.newSubtable(4)
    newtable.platformID = table.platformID
    newtable.platEncID = table.platEncID
    newtable.language = table.language
    newtable.cmap = table.cmap
    outtables.append(newtable)
  font['cmap'].tables = outtables
  return fixit


def remove_cmap_subtable(font, plat_id, enc_id):
  to_be_removed = []
  for index, table in enumerate(font['cmap'].tables):
    if table.platformID == plat_id and table.platEncID == enc_id:
      to_be_removed.append(index)

  to_be_removed.reverse()
  for index in to_be_removed:
    font['cmap'].tables.remove(table)

  fixit = len(to_be_removed) > 0
  return fixit


def keep_only_specific_cmap(font, plat_id, enc_id=None):
  to_be_removed = []
  for index, table in enumerate(font['cmap'].tables):
    if table.platformID != plat_id and (enc_id==None or table.platEncID != enc_id):
      to_be_removed.append(index)
    else:
      print(("Keeping format {} cmap subtable with Platform ID = {}"
             " and Encoding ID = {}").format(table.format,
                                             table.platformID,
                                             table.platEncID))

  to_be_removed.reverse()
  for index in to_be_removed:
    table = font['cmap'].tables[index]
    print(("--- Removed format {} cmap subtable with Platform ID = {}"
           " and Encoding ID = {} ---").format(table.format,
                                               table.platformID,
                                               table.platEncID))
    font['cmap'].tables.remove(table)

  fixit = len(to_be_removed) > 0
  return fixit


def main():
  parser = ArgumentParser(description=description)
  parser.add_argument('fonts', nargs='+')
  parser.add_argument('--format-4-subtables', '-f4', default=False,
                      action='store_true',
                      help="Convert cmap subtables to format 4")
  parser.add_argument('--drop-mac-subtable', '-dm', default=False,
                      action='store_true',
                      help='Drop Mac cmap subtables')
  parser.add_argument('--keep-only-pid-0', '-k0', default=False,
                      action='store_true',
                      help=('Keep only cmap subtables with pid=0'
                            ' and drop the rest.'))
  args = parser.parse_args()

  for path in args.fonts:
    font = TTFont(path)
    font_filename = basename(path)
    fixit = False

    if args.format_4_subtables:
      print('\nConverting Cmap subtables to format 4...')
      fixit = convert_cmap_subtables_to_v4(font)

    if args.keep_only_pid_0:
      print('\nDropping all Cmap subtables,'
            ' except the ones with PlatformId = 0...')
      dropped = keep_only_specific_cmap(font, 0)
      fixit = fixit or dropped
    elif args.drop_mac_subtable:
      print('\nDropping any Cmap Mac subtable...')
      dropped = remove_cmap_subtable(font, 1, 0)
      fixit = fixit or dropped

    if fixit:
      print('\n\nSaving %s to %s.fix' % (font_filename, path))
      font.save(path + '.fix')
    else:
      print('\n\nThere were no changes needed on the font file!')


if __name__ == '__main__':
  main()
