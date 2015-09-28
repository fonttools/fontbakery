#!/usr/bin/env python
from __future__ import print_function
import argparse
import csv
import os
import sys
import tabulate

from fontTools import ttLib

args = argparse.ArgumentParser(
    description='Print out usWidthClass of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')
args.add_argument('--set', type=int, default=0)
args.add_argument('--autofix', default=False, action='store_true')


def print_info(fonts, print_csv=False):
    headers = ['filename', 'usWidthClass']
    rows = []
    warnings = []
    for font in fonts:
        ttfont = ttLib.TTFont(font)
        usWidthClass = ttfont['OS/2'].usWidthClass
        rows.append([os.path.basename(font), usWidthClass])
        if usWidthClass != 5:
            warning = "WARNING: {} is {}, expected 5"
            warnings.append(warning.format(font, usWidthClass))

    def as_csv(rows):
        writer = csv.writer(sys.stdout)
        writer.writerows([headers])
        writer.writerows(rows)
        sys.exit(0)

    if print_csv:
        as_csv(rows)
        
    print(tabulate.tabulate(rows, headers, tablefmt="pipe"))
    for warn in warnings:
        print(warn, file=sys.stderr)


def getFromFilename(filename):
    if "UltraCondensed-" in filename:
        usWidthClass = 1
    elif "ExtraCondensed-" in filename:
        usWidthClass = 2
    elif "SemiCondensed-" in filename:
        usWidthClass = 4
    elif "Condensed-" in filename:
        usWidthClass = 3
    elif "SemiExpanded-" in filename:
        usWidthClass = 6
    elif "ExtraExpanded-" in filename:
        usWidthClass = 8
    elif "UltraExpanded-" in filename:
        usWidthClass = 9
    elif "Expanded-" in filename:
        usWidthClass = 7
    else:
        usWidthClass = 5
    return usWidthClass


def fix(fonts, value=None):
    rows = []
    headers = ['filename', 'usWidthClass was', 'usWidthClass now']

    for font in fonts:
        row = [font]
        ttfont = ttLib.TTFont(font)
        if not value:
            usWidthClass = getFromFilename(font)
        else:
            usWidthClass = value
        row.append(ttfont['OS/2'].usWidthClass)
        ttfont['OS/2'].usWidthClass = usWidthClass
        row.append(ttfont['OS/2'].usWidthClass)
        ttfont.save(font + '.fix')
        rows.append(row)

    if rows:
        print(tabulate.tabulate(rows, headers, tablefmt="pipe"))


if __name__ == '__main__':
    arg = args.parse_args()
    if arg.autofix:
        fix(arg.font)
        sys.exit(0)
    if arg.set:
        fix(arg.font, value=int(arg.set))
        sys.exit(0)
    print_info(arg.font, print_csv=arg.csv)
    
    