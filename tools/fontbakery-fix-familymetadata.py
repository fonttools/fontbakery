#!/usr/bin/env python
import argparse
import os

from fontTools import ttLib
import tabulate

args = argparse.ArgumentParser(
    description='Print out family metadata of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')


def getByte2(i_value):
    return i_value >> 8


def getByte1(i_value):
    return i_value & 255



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

    def putfsSelection(self, ttfont):
        self.addToHeader('fsSelection')
        args = getByte2(ttfont['OS/2'].fsSelection), getByte1(ttfont['OS/2'].fsSelection)
        self.current_row.append('{:#010b} {:#010b}'.format(*args).replace('0b', ''))

    def putmacStyle(self, ttfont):
        self.addToHeader('macStyle')
        value = ttfont['head'].macStyle
        args = getByte2(value), getByte1(value)
        self.current_row.append('{:#010b} {:#010b}'.format(*args).replace('0b', ''))

    def putnameIds(self, ttfont, platform=3):
        nameids = ['1', '2', '4', '6', '16', '17', '18']
        row = []
        for nameid in nameids:
            value = ''
            for name in ttfont['name'].names:
                if str(name.nameID) == nameid and platform == name.platformID:
                    if name.isUnicode():
                        value = name.string.decode("utf-16-be") or ''
                    else:
                        value = name.string or ''
                    break

            self.addToHeader('id{}'.format(nameid))
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

    arg = args.parse_args()
    
    rows = []
    fm = FamilyMetadataTable()
    for i, font in enumerate(arg.font):
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

    if arg.csv:
        as_csv(fm.rows)

    print(tabulate.tabulate(fm.rows, fm.headers))