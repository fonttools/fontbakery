#!/usr/bin/env python
import argparse
import os
import tabulate

from fontTools import ttLib
from bakery_cli.fixers import RemoveNameRecordWithPlatformID_1_Fixer

args = argparse.ArgumentParser(
    description='Print out nameIDs strings of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--autofix', default=False, action='store_true', help='Apply autofix')
args.add_argument('--csv', default=False, action='store_true', help='Output data in comma-separate-values (CSV) file format')
args.add_argument('--id', '-i', default='all')
args.add_argument('--platform', '-p', type=int, default=3)

if __name__ == '__main__':

    arg = args.parse_args()

    nameids = ['1', '2', '4', '6', '16', '17', '18']
    user_nameids = [x.strip() for x in arg.id.split(',')]

    if 'all' not in user_nameids:
        nameids = set(nameids) & set(user_nameids)

    rows = []
    for font in arg.font:
        ttfont = ttLib.TTFont(font)
        row = [os.path.basename(font)]
        for name in ttfont['name'].names:
            if str(name.nameID) not in nameids or name.platformID != arg.platform:
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

    if arg.csv:
        as_csv(rows)

    print(tabulate.tabulate(rows, header, tablefmt="pipe"))

    for path in arg.font:
        if arg.autofix:
            fixer = RemoveNameRecordWithPlatformID_1_Fixer(None, path)
            fixer.apply()