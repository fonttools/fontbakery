#!/usr/bin/env python
import argparse
import csv
import os
import sys

from fontTools import ttLib
import tabulate

args = argparse.ArgumentParser(
	description='Print out fsSelection bitmask of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')
args.add_argument('--autofix', default=False, action='store_true')


def getByte2(ttfont):
	return ttfont['OS/2'].fsSelection >> 8


def getByte1(ttfont):
	return ttfont['OS/2'].fsSelection & 255


def printInfo(fonts, print_csv=False):
	rows = []
	headers = ['filename', 'fsSelection']
	for font in fonts:
		ttfont = ttLib.TTFont(font)
		row = [os.path.basename(font)]
		row.append('{:#010b} {:#010b}'.format(getByte2(ttfont), getByte1(ttfont)).replace('0b', ''))
		rows.append(row)

	def as_csv(rows):
		writer = csv.writer(sys.stdout)
		writer.writerows([headers])
		writer.writerows(rows)
		sys.exit(0)

	if print_csv:
		as_csv(rows)
	else:
		print(tabulate.tabulate(rows, headers))


if __name__ == '__main__':
	arg = args.parse_args()
	if arg.autofix:
		for font in arg.font:
			ttfont = ttLib.TTFont(font)
			if '-Regular' in font:
				ttfont['OS/2'].fsSelection |= 0b1000000
			if '-Bold' in font:
				ttfont['OS/2'].fsSelection |= 0b100000
			if 'Italic' in font:
				ttfont['OS/2'].fsSelection |= 0b1
			ttfont.save(font + '.fix')
	printInfo(arg.font, print_csv=arg.csv)
	
	