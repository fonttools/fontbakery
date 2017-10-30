#!/usr/bin/env python
import argparse
import os
import tabulate
from fontTools import ttLib

args = argparse.ArgumentParser(
    description='Print out italicAngle of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')

if __name__ == '__main__':
    arg = args.parse_args()

    headers = ['filename', 'italicAngle']
    rows = []
    for font in arg.font:
        ttfont = ttLib.TTFont(font)
        rows.append([os.path.basename(font), ttfont['post'].italicAngle])

    if arg.csv:
        import csv
        writer = csv.writer(sys.stdout)
        writer.writerows([headers])
        writer.writerows(rows)
    else:
        print(tabulate.tabulate(rows, headers, tablefmt="pipe"))
