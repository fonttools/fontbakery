#!/usr/bin/env python
import argparse
import os
import tabulate
from fontTools import ttLib

parser = argparse.ArgumentParser(description='Print out nameID'
                                             ' strings of the fonts')
parser.add_argument('font', nargs="+")
parser.add_argument('--autofix', default=False,
                    action='store_true', help='Apply autofix')
parser.add_argument('--csv', default=False, action='store_true',
                    help="Output data in comma-separate-values"
                         " (CSV) file format")
parser.add_argument('--id', '-i', default='all')
parser.add_argument('--platform', '-p', type=int, default=3)


def main():
    args = parser.parse_args()
    nameids = ['1', '2', '4', '6', '16', '17', '18']
    user_nameids = [x.strip() for x in args.id.split(',')]

    if 'all' not in user_nameids:
        nameids = set(nameids) & set(user_nameids)

    rows = []
    for font in args.font:
        ttfont = ttLib.TTFont(font)
        row = [os.path.basename(font)]
        for name in ttfont['name'].names:
            if str(name.nameID) not in nameids or\
               name.platformID != args.platform:
                continue

            value = name.string.decode(name.getEncoding()) or ''
            row.append(value)

        rows.append(row)

    header = ['filename'] + ['id' + x for x in nameids]

    def as_csv(rows):
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerows([header])
        writer.writerows(rows)
        sys.exit(0)

    if args.csv:
        as_csv(rows)

    print(tabulate.tabulate(rows, header, tablefmt="pipe"))

    for path in args.font:
        if args.autofix:
            font = ttLib.TTFont(path)
            saveit = False
            for name in font['name'].names:
                if name.platformID != 1:
                    saveit = True
                    del name
            if saveit:
                font.save(path + ".fix")

if __name__ == '__main__':
  main()

