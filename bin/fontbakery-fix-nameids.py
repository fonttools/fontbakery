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
parser.add_argument('--drop-superfluous-mac-names', '-m', default=False,
                    action='store_true',
                    help='Drop superfluous Mac names')


def has_mac_names(ttfont):
    """Check if a font has Mac names. Mac names have the following
    field values:
    platformID: 1, encodingID: 0, LanguageID: 0"""
    for i in range(255):
        if ttfont['name'].getName(i, 1, 0, 0):
            return True
    return False


def drop_superfluous_mac_names(ttfont):
    """Drop superfluous Mac nameIDs.

    The following nameIDS are kept:
    1: Font Family name,
    2: Font Family Subfamily name,
    3: Unique font identifier,
    4: Full font name,
    5: Version string,
    6: Postscript name,
    16: Typographic family name,
    17: Typographic Subfamily name
    18: Compatible full (Macintosh only),
    20: PostScript CID,
    21: WWS Family Name,
    22: WWS Subfamily Name,
    25: Variations PostScript Name Prefix.

    We keep these IDs in order for certain application to still function
    such as Word 2011. IDs 1-6 are very common, > 16 are edge cases.

    https://www.microsoft.com/typography/otspec/name.htm"""
    keep_ids = [1, 2, 3, 4, 5, 6, 16, 17, 18, 20, 21, 22, 25]
    for n in range(255):
        if n not in keep_ids:
            name = ttfont['name'].getName(n, 1, 0, 0)
            if name:
                ttfont['name'].names.remove(name)


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
        font = ttLib.TTFont(path)
        saveit = False

        if args.autofix:
            for name in font['name'].names:
                if name.platformID != 1:
                    saveit = True
                    del name

        if args.drop_superfluous_mac_names:
            if has_mac_names(font):
                drop_superfluous_mac_names(font)
                saveit = True
            else:
                print('font %s has no mac nametable' % path)

        if saveit:
                font.save(path + ".fix")


if __name__ == '__main__':
    main()
