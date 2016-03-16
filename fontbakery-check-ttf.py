#!/usr/bin/env python2

__author__="The Font Bakery Authors"

import os, sys, argparse, glob, logging

from fontTools import ttLib

def main():
  # set up a basic logging config
  # to include timestamps
  # log_format = '%(asctime)s %(levelname)-8s %(message)s'
  log_format = '%(levelname)-8s %(message)s  '
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
  parser.add_argument('filenames', nargs='+', 
    help='file name(s) of fonts to check. Wildcards like *.ttf are allowed.')
  args = parser.parse_args()

  logging.debug("Checking each file is a ttfs")
  fonts_to_check = []
  for filename in sorted(args.filenames):
    # use glob.glob to accept *.ttf
    for font_file in glob.glob(filename):
      if font_file.endswith('.ttf'):
        fonts_to_check.append(font_file)
      else:
        file_path, filename = os.path.split(font_file)
        logging.error("Skipping " + filename + " as not a ttf") 
  fonts_to_check.sort()

  logging.debug("Checking files are named canonically")
  not_canonical = []
  for font_file in fonts_to_check:
    file_path, filename = os.path.split(font_file)
    filename_base, filename_extention = os.path.splitext(filename)
    family, style = filename_base.split('-')
    style_names = ["Thin", "ExtraLight", "Light", "Regular", "Medium", 
             "SemiBold", "Bold", "ExtraBold", "Black", 
             "Thin Italic", "ExtraLight Italic", "Light Italic", 
             "Italic", "Medium Italic", "SemiBold Italic", 
             "Bold Italic", "ExtraBold Italic", "Black Italic"]
    # remove spaces
    style_file_names = [name.replace(' ', '') for name in style_names]
    if style in style_file_names:
      logging.info(font_file + " is named canonically")
    else:
        logging.critical(font_file + " is not named canonically")
        not_canonical.append(font_file)
  if not_canonical:
    print '\nAborted, critical errors. Please rename these files canonically and try again:\n ',
    print '\n  '.join(not_canonical)
    print '\nCanonical names are defined in',
    print 'https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md#instance-and-file-naming'
    sys.exit(1)

  for font_file in fonts_to_check:
    logging.debug("Opening " + font_file)
    font = ttLib.TTFont(font_file)
    logging.info(font_file + " opened")

    logging.debug("Checking OS/2 table")
    if font['OS/2'].fsType != 0:
      logging.warning("fsType is not 0")
      font['OS/2'].fsType = 0
      logging.info("HOTFIX: fsType is now 0")
    else:
      logging.info("fsType is 0")
      
    logging.info("TODO: Check fsSelection")
    logging.info("TODO: Check head table")
    logging.info("TODO: Check name table")
    
    # TODO Fix https://github.com/googlefonts/fontbakery/issues/748 here
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
    logging.info(font_file_output + " saved\n")

if __name__=='__main__':
    main()