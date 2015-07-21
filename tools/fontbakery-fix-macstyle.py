#!/usr/bin/env python
import argparse
import logging
import os
import tabulate

from bakery_cli.logger import logger
from fontTools import ttLib

args = argparse.ArgumentParser(
	description='Print out macStyle bitmask of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--csv', default=False, action='store_true')
args.add_argument('--verbose', default=False, action='store_true')


def getByte2(ttfont):
	return ttfont['head'].macStyle >> 8


def getByte1(ttfont):
	return ttfont['head'].macStyle & 255


if __name__ == '__main__':

	arg = args.parse_args()

	if not arg.verbose:
	    logger.setLevel(logging.INFO)
	
	rows = []
	headers = ['filename', 'macStyle']
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