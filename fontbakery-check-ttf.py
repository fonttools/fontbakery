#!/usr/bin/env python2

__author__="The Font Bakery Authors"

import argparse
import glob
import os
import logging

from fontTools import ttLib

def main():
    # set up a basic logging config
    # to include timestamps
    # log_format = '%(asctime)s %(levelname)-8s %(message)s'
    log_format = '%(levelname)-8s %(message)s'
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # to show all log events
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    
    # set up some command line argument processing
    parser = argparse.ArgumentParser(description="Check TTF files for common issues.")
    parser.add_argument('filenames', nargs='+', help='file name(s) of fonts to check')
    args = parser.parse_args()

    # open each file and if it is a ttf, check it
    for filename in args.filenames:
        for font_file in glob.glob(filename):
            if font_file[-3:] == "ttf":
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
      logging.info("HOTFIX: fsType is now 0")
    else:
      logging.info("fsType is 0")
      
    logging.info("TODO: Check fsSelection")
    logging.info("TODO: Check head table")
    logging.info("TODO: Check name table")
    
    logging.debug("Checking name table for items without platformID=1")
    new_names = []
    for name in font['name'].names:
      if name.platformID != 1:
        non_pid1 = True
        new_names.append(name)
    if non_pid1:
      logging.error("name table for items without platformID=1 exist")
      font['name'].names = new_names
      logging.error("HOTFIX: name table items with platformID=1 removed")
    else:
      logging.info("No name table for items without platformID=1")

    # more checks go above this line

    font_file_output = font_file + '.fix'
    font.save(font_file_output)
    font.close()
    logging.info(font_file_output + " saved")

if __name__=='__main__':
    main()