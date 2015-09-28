#!/usr/bin/env python
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


def print_info(fonts, print_csv=False):
	headers = ['filename', 'usWidthClass']
	rows = []
	for font in fonts:
		ttfont = ttLib.TTFont(font)
		rows.append([os.path.basename(font), ttfont['OS/2'].usWidthClass])

	def as_csv(rows):
		writer = csv.writer(sys.stdout)
		writer.writerows([headers])
		writer.writerows(rows)
		sys.exit(0)

	if print_csv:
		as_csv(rows)
		
	print(tabulate.tabulate(rows, headers, tablefmt="pipe"))


if __name__ == '__main__':
	arg = args.parse_args()
	print_info(arg.font, print_csv=arg.csv)
	
	