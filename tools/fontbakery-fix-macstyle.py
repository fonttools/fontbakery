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
args.add_argument('--bit-bold', choices=[0, 1], type=int)
args.add_argument('--bit-italic', choices=[0, 1], type=int)
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

	print(tabulate.tabulate(rows, headers, tablefmt="pipe"))


def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)


if __name__ == '__main__':

	arg = args.parse_args()
	if arg.autofix or arg.bit_bold != -1 or arg.bit_italic != -1:
		for font in arg.font:
			ttfont = ttLib.TTFont(font)
			if '-Bold' in font:
				ttfont['head'].macStyle |= 0b1
			if arg.bit_bold:
				ttfont['head'].macStyle |= 0b1
			if arg.bit_bold == 0:
				ttfont['head'].macStyle = clearBit(ttfont['head'].macStyle, 0)
			if 'Italic' in font:
				ttfont['head'].macStyle |= 0b10
			if arg.bit_italic:
				ttfont['head'].macStyle |= 0b10
			if arg.bit_italic == 0:
				ttfont['head'].macStyle = clearBit(ttfont['head'].macStyle, 1)
			ttfont.save(font + '.fix')
		printInfo([f + '.fix' for f in arg.font], print_csv=arg.csv)
		sys.exit(0)

	printInfo(arg.font, print_csv=arg.csv)