#!/usr/bin/env python2

__author__="The Font Bakery Authors"

import argparse
import glob
import os
import logging

from fontTools import ttLib

def main():
    # set up a basic logging config
    log_format = '%(levelname)s %(message)s'
    logging.basicConfig(format=log_format, level=logging.DEBUG)
    
    # set up some command line argument processing
    parser = argparse.ArgumentParser(description="Check TTF files for common issues.")
    parser.add_argument('filenames', nargs='+', help='file name(s) of fonts to check')
    args = parser.parse_args()

    # open each file and if it is a ttf, check it
    for filename in args.filenames:
        for font_file in glob.glob(filename):
            if file_file[:3] == "ttf":
                check(font_file)
            else:
                logging.error(font_file + "is not a ttf, skipping")

def check(font_file):
    logging.debug("Opening " + font_file)
    font = ttLib.TTFont(font_file)
    logging.info(font_file + " opened")

    # OS/2 Table Checks
    logging.debug("Checking OS/2 fsType")
    if font['OS/2'].fsType != 0:
      logging.warning("fsType is not 0")
      font['OS/2'].fsType = 0
      logging.info("fsType is now 0, hotfixed")
    else:
      logging.info("fsType is 0")
      
    logging.info("TODO: Check fsSelection")
    logging.info("TODO: Check head table")
    logging.info("TODO: Check name table")

    # more checks go above this line

    font_file_output = font_file + '.fix'
    font.save(font_file_output)
    font.close()
    logging.info(font_file_output + " saved")

if __name__=='__main__':
    main()