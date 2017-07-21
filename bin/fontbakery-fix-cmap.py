#!/usr/bin/env python
from ntpath import basename
from argparse import ArgumentParser
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable


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
  parser = ArgumentParser()
  parser.add_argument('fonts', nargs='+')
  parser.add_argument('--format-4-subtables', '-f4', default=False, action='store_true')
  parser.add_argument('-drop-mac-subtable', '-dm', default=False,
                      action='store_true')
  args = parser.parse_args()
  
  for path in args.fonts:
    font = TTFont(path)
    font_filename = basename(font)
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
