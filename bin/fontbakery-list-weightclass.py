#!/usr/bin/env python
import argparse
import os
import tabulate
from fontTools import ttLib

parser = argparse.ArgumentParser(description='Print out'
                                             ' usWeightClass of the fonts')
parser.add_argument('font', nargs="+")
parser.add_argument('--csv', default=False, action='store_true')


def main():
  args = parser.parse_args()
  headers = ['filename', 'usWeightClass']
  rows = []
  for font in args.font:
    ttfont = ttLib.TTFont(font)
    rows.append([os.path.basename(font), ttfont['OS/2'].usWeightClass])

  def as_csv(rows):
    import csv
    import sys
    writer = csv.writer(sys.stdout)
    writer.writerows([headers])
    writer.writerows(rows)
    sys.exit(0)

  if args.csv:
    as_csv(rows)

  print(tabulate.tabulate(rows, headers, tablefmt="pipe"))

if __name__ == '__main__':
  main()

