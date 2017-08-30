#!/usr/bin/env python
import argparse
import os
import tabulate
from fontTools import ttLib
from fontbakery.constants import (PLATFORM_ID__WINDOWS,
                                  NAMEID_STR,
                                  NAMEID_FONT_FAMILY_NAME,
                                  NAMEID_FONT_SUBFAMILY_NAME,
                                  NAMEID_FULL_FONT_NAME,
                                  NAMEID_POSTSCRIPT_NAME,
                                  NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                                  NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME,
                                  NAMEID_COMPATIBLE_FULL_MACONLY)

parser = argparse.ArgumentParser(description=("Print out family"
                                              " metadata of the fonts"))
parser.add_argument('font', nargs="+")
parser.add_argument('--csv', default=False, action='store_true')


class FamilyMetadataTable(object):
    headers = ['filename']
    rows = []
    current_row = []

    def addToHeader(self, value):
        if value not in self.headers:
            self.headers.append(value)

    def putnewRow(self, columnvalue=None):
        self.current_row = []
        if columnvalue:
            self.current_row.append(columnvalue)

    def putrowToTable(self):
        self.rows.append(self.current_row)

    def binary_string(self, value):
        return "{:#010b} {:#010b}".format(value >> 8,
                                          value & 0xFF).replace('0b', '')
    def putfsSelection(self, ttfont):
        self.addToHeader('fsSelection')
        self.current_row.append(self.binary_string(ttfont['OS/2'].fsSelection))

    def putmacStyle(self, ttfont):
        self.addToHeader('macStyle')
        self.current_row.append(self.binary_string(ttfont['head'].macStyle))

    def putnameIds(self, ttfont, platform=PLATFORM_ID__WINDOWS):
        for nameid in [NAMEID_FONT_FAMILY_NAME,
                       NAMEID_FONT_SUBFAMILY_NAME,
                       NAMEID_FULL_FONT_NAME,
                       NAMEID_POSTSCRIPT_NAME,
                       NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                       NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME,
                       NAMEID_COMPATIBLE_FULL_MACONLY]:
            value = ''
            for name in ttfont['name'].names:
                if nameid == name.nameID and platform == name.platformID:
                    value = name.string.decode(name.getEncoding()) or ''
                    break

            self.addToHeader('{}:{}'.format(nameid, NAMEID_STR[nameid]))
            self.current_row.append(value)

    def putitalicAngle(self, ttfont):
        self.addToHeader('italicAngle')
        self.current_row.append(ttfont['post'].italicAngle)

    def putwidthClass(self, ttfont):
        self.addToHeader('usWidthClass')
        self.current_row.append(ttfont['OS/2'].usWidthClass)

    def putweightClass(self, ttfont):
        self.addToHeader('usWeightClass')
        self.current_row.append(ttfont['OS/2'].usWeightClass)

    def putPanose(self, ttfont):
        for i, k in enumerate(sorted(ttfont['OS/2'].panose.__dict__.keys())):
            self.addToHeader(k)
            self.current_row.append(getattr(ttfont['OS/2'].panose, k, 0))

    def putfixedPitch(self, ttfont):
        self.addToHeader('isFixedPitch')
        self.current_row.append(ttfont['post'].isFixedPitch)


if __name__ == '__main__':
    options = parser.parse_args()
    rows = []
    fm = FamilyMetadataTable()
    for i, font in enumerate(options.font):
        ttfont = ttLib.TTFont(font)
        fm.putnewRow(os.path.basename(font))
        fm.putnameIds(ttfont)
        fm.putmacStyle(ttfont)
        fm.putitalicAngle(ttfont)
        fm.putfsSelection(ttfont)
        fm.putweightClass(ttfont)
        fm.putwidthClass(ttfont)
        fm.putfixedPitch(ttfont)
        fm.putPanose(ttfont)
        fm.putrowToTable()

    def as_csv(rows):
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerows([fm.headers])
        writer.writerows(rows)
        sys.exit(0)

    if options.csv:
        as_csv(fm.rows)

    print(tabulate.tabulate(fm.rows, fm.headers))

