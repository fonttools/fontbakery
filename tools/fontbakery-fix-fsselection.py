#!/usr/bin/env python
import argparse
import logging
import os

from bakery_cli.logger import logger
from fontTools import ttLib
import tabulate

args = argparse.ArgumentParser(
	description='Print out fsSelection bitmask of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--verbose', default=False, action='store_true')


def getByte2(ttfont):
	return ttfont['OS/2'].fsSelection >> 8


def getByte1(ttfont):
	return ttfont['OS/2'].fsSelection & 255


if __name__ == '__main__':

	arg = args.parse_args()

	if not arg.verbose:
	    logger.setLevel(logging.INFO)
	
	rows = []
	headers = ['filename', 'byte_2', 'byte_1']
	for font in arg.font:
		ttfont = ttLib.TTFont(font)
		row = [os.path.basename(font)]
		row.append('{:#010b}'.format(getByte2(ttfont)).replace('0b', ''))
		row.append('{:#010b}'.format(getByte1(ttfont)).replace('0b', ''))
		rows.append(row)

	print(tabulate.tabulate(rows, headers))