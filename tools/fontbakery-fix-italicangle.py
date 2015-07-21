#!/usr/bin/env python
import argparse
import os
import tabulate

from fontTools import ttLib

args = argparse.ArgumentParser(
	description='Print out italicAngle of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')


if __name__ == '__main__':

	arg = args.parse_args()
	
	headers = ['filename', 'italicAngle']
	rows = []
	for font in arg.font:
		ttfont = ttLib.TTFont(font)
		rows.append([os.path.basename(font), ttfont['post'].italicAngle])

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