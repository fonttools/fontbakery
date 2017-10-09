#!/usr/bin/env python
import argparse
import os
import tabulate
from fontTools import ttLib
from fontbakery.constants import (NAMEID_COPYRIGHT_NOTICE,
                                  PLATID_STR)

parser = argparse.ArgumentParser(description='Print out copyright'
                                             ' nameIDs strings')
parser.add_argument('font', nargs="+")
parser.add_argument('--csv', default=False, action='store_true',
                    help="Output data in comma-separate-values"
                         " (CSV) file format")


def main():
    args = parser.parse_args()

    rows = []
    for font in args.font:
        ttfont = ttLib.TTFont(font)
        for name in ttfont['name'].names:
            if name.nameID != NAMEID_COPYRIGHT_NOTICE:
                continue

            value = name.string.decode(name.getEncoding()) or ''
            rows.append([os.path.basename(font),
                         value,
                         len(value),
                         "{} ({})".format(
                             name.platformID,
                             PLATID_STR.get(name.platformID, "?"))])

    header = ['filename', 'copyright notice', 'char length', 'platformID']

    def as_csv(rows):
        import csv
        import sys
        writer = csv.writer(sys.stdout, 
                            delimiter='|',
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows([header])
        writer.writerows(rows)
        sys.exit(0)

    if args.csv:
        as_csv(rows)

    print("") #some spacing
    print(tabulate.tabulate(rows, header, tablefmt="pipe"))
    print("") #some spacing

if __name__ == '__main__':
  """ Example usage:

      fontbakery-check-copyright-notices.py ~/fonts/*/*/*ttf --csv > ~/notices.txt;
  """
  main()
