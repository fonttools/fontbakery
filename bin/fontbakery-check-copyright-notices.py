#!/usr/bin/env python3
import argparse
import os
import tabulate
from fontTools import ttLib

parser = argparse.ArgumentParser(description='Print out copyright'
                                             'nameIDs strings')
parser.add_argument('font', nargs="+")
parser.add_argument('--csv', default=False, action='store_true',
                    help="Output data in comma-separate-values"
                         " (CSV) file format")


def main():
    args = parser.parse_args()
    nameids = '0'

    rows = []
    for font in args.font:
        ttfont = ttLib.TTFont(font)
        row = [os.path.basename(font)]
        for name in ttfont['name'].names:
            if str(name.nameID) not in nameids:
                continue

            value = name.string.decode(name.getEncoding()) or ''
            row.append(value)
            row.append(len(value))

        rows.append(row)

    header = ['filename', 'copyright notice', 'char length']

    def as_csv(rows):
        import csv
        import sys
        writer = csv.writer(sys.stdout, 
                                delimiter='|',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows([header])
        writer.writerows(rows)
        sys.exit(0)

    if args.csv:
        as_csv(rows)

    print(tabulate.tabulate(rows, header, tablefmt="pipe"))

if __name__ == '__main__':
  """
    
    Example usage: 
    
    fontbakery-check-copyright-notices.py ~/fonts/*/*/*ttf --csv > ~/notices.txt;
  
  """
  main()
