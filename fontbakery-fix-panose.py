#!/usr/bin/env python
import argparse
import os
import tabulate
from fontTools import ttLib

args = argparse.ArgumentParser(
    description='Print out Panose of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')

if __name__ == '__main__':
    arg = args.parse_args()

    headers = ['filename']
    rows = []
    for i, font in enumerate(arg.font):
        row = [os.path.basename(font)]

        ttfont = ttLib.TTFont(font)

        for k in sorted(ttfont['OS/2'].panose.__dict__.keys()):
            if i < 1:
                headers.append(k)
            row.append(getattr(ttfont['OS/2'].panose, k, 0))
        rows.append(row)

    def as_csv(rows):
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerows([headers])
        writer.writerows(rows)
        sys.exit(0)

    if arg.csv:
        as_csv(rows)

    print(tabulate.tabulate(rows, headers, tablefmt="pipe"))
