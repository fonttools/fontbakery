#!/usr/bin/env python
import argparse
import os

from fontTools import ttLib
import tabulate

args = argparse.ArgumentParser(
	description='Print out fsSelection bitmask of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')


def getByte2(ttfont):
	return ttfont['OS/2'].fsSelection >> 8


def getByte1(ttfont):
	return ttfont['OS/2'].fsSelection & 255


if __name__ == '__main__':

	arg = args.parse_args()
	
	rows = []
	headers = ['filename', 'fsSelection']
	for font in arg.font:
		ttfont = ttLib.TTFont(font)
		row = [os.path.basename(font)]
		row.append('{:#010b} {:#010b}'.format(getByte2(ttfont), getByte1(ttfont)).replace('0b', ''))
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

	print(tabulate.tabulate(rows, headers))