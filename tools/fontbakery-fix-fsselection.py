#!/usr/bin/env python
import argparse
import logging
import os

from bakery_cli.logger import logger
from fontTools import ttLib

args = argparse.ArgumentParser(
	description='Print out fsSelection bitmask of the fonts')
args.add_argument('font', nargs="+")
args.add_argument('--verbose', default=False, action='store_true')


def getByte2(ttfont):
	return ttfont['OS/2'].fsSelection >> 8


def getByte1(ttfont):
	return ttfont['OS/2'].fsSelection & 255


def format_str_fsselection(font):
	ttfont = ttLib.TTFont(font)
	byte_1 = getByte1(ttfont)
	byte_2 = getByte2(ttfont)
	basename = os.path.basename(font)

	msg = '{}: {:#010b} {:#08b}'.format(basename, byte_2, byte_1)
	return msg.replace('0b', '')


if __name__ == '__main__':

	arg = args.parse_args()

	if not arg.verbose:
	    logger.setLevel(logging.INFO)
	
	for font in arg.font:
		logger.info(format_str_fsselection(font))