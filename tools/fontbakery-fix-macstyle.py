#!/usr/bin/env python
import argparse
import csv
import logging
import os
import sys
import tabulate

from fontTools import ttLib

args = argparse.ArgumentParser(
	description='Print out macStyle bitmask of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')
args.add_argument('--bit-bold', default=False, action='store_true')
args.add_argument('--bit-italic', default=False, action='store_true')
args.add_argument('--autofix', default=False, action='store_true')


def getByte2(ttfont):
	return ttfont['head'].macStyle >> 8


def getByte1(ttfont):
	return ttfont['head'].macStyle & 255


def printInfo(fonts, print_csv=False):
	rows = []
	headers = ['filename', 'macStyle']
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

	print(tabulate.tabulate(rows, headers))


if __name__ == '__main__':

	arg = args.parse_args()
	if arg.autofix:
		for font in arg.font:
			ttfont = ttLib.TTFont(font)
			if '-Bold' in font or arg.bit_bold:
				ttfont['head'].macStyle |= 0b1
			if 'Italic' in font or arg.bit_italic:
				ttfont['head'].macStyle |= 0b10
			ttfont.save(font + '.fix')
		printInfo([f + '.fix' for f in arg.font], print_csv=arg.csv)
		sys.exit(0)

	printInfo(arg.font, print_csv=arg.csv)