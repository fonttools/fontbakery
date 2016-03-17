#!/usr/bin/env python2

__author__="The Font Bakery Authors"

import os, sys, argparse, glob, logging, requests, subprocess
from bs4 import BeautifulSoup

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

  #------------------------------------------------------
  logging.debug("Checking each file is a ttfs")
  fonts_to_check = []
  for filename in sorted(args.filenames):
    # use glob.glob to accept *.ttf
    for font_file in glob.glob(filename):
      if font_file.endswith('.ttf'):
        fonts_to_check.append(font_file)
      else:
        file_path, filename = os.path.split(font_file)
        logging.warning("Skipping " + filename + " as not a ttf") 
  fonts_to_check.sort()

  #------------------------------------------------------
  logging.debug("Checking files are named canonically")
  not_canonical = []
  style_names = ["Thin", 
                 "ExtraLight", 
                 "Light", 
                 "Regular", 
                 "Medium", 
                 "SemiBold", 
                 "Bold", 
                 "ExtraBold", 
                 "Black", 
                 "Thin Italic", 
                 "ExtraLight Italic", 
                 "Light Italic", 
                 "Italic", 
                 "Medium Italic", 
                 "SemiBold Italic", 
                 "Bold Italic", 
                 "ExtraBold Italic", 
                 "Black Italic"
                ]
  for font_file in fonts_to_check:
    file_path, filename = os.path.split(font_file)
    filename_base, filename_extention = os.path.splitext(filename)
    # remove spaces
    style_file_names = [name.replace(' ', '') for name in style_names]
    try: 
      family, style = filename_base.split('-')
      if style in style_file_names:
        logging.info("OK: {} is named canonically".format(font_file))
      else:
        logging.critical("{} is not named canonically".format(font_file))
        not_canonical.append(font_file)
    except:
        logging.critical("{} is not named canonically".format(font_file))
        not_canonical.append(font_file)
  if not_canonical:
    print '\nAborted, critical errors with filenames. Please rename these files canonically and try again:\n ',
    print '\n  '.join(not_canonical)
    print '\nCanonical names are defined in',
    print 'https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md#instance-and-file-naming'
    sys.exit(1)

  #------------------------------------------------------
  # TODO: cache this in /tmp so its only requested once per boot
  logging.debug("Fetching Microsoft's vendorID list")
  url = 'https://www.microsoft.com/typography/links/vendorlist.aspx'
  registered_vendor_ids = {}
  try:
    req = requests.get(url, auth=('user', 'pass'))
    soup = BeautifulSoup(req.content, 'html.parser')
    table = soup.find(id="VendorList")
    try:
      for row in table.findAll('tr'):
        cells = row.findAll('td')
        code = cells[0].string
        labels = [label for label in cells[1].stripped_strings]
        registered_vendor_ids[code] = labels[0]
    except:
      logging.warning("Failed to parse Microsoft's vendorID list.")
  except:
    logging.warning("Failed to fetch Microsoft's vendorID list.")

  #------------------------------------------------------
  for font_file in fonts_to_check:
    logging.debug("Opening " + font_file)
    font = ttLib.TTFont(font_file)

    #----------------------------------------------------
    logging.debug("Checking OS/2 fsType")
    if font['OS/2'].fsType != 0:
      logging.error("OS/2 fsType is not 0")
      font['OS/2'].fsType = 0
      logging.info("HOTFIX: OS/2 fsType is now 0")
    else:
      logging.info("OK: fsType is 0")

    #----------------------------------------------------
    logging.debug("Checking OS/2 achVendID")
    vid = font['OS/2'].achVendID
    if len(registered_vendor_ids.keys()) > 0:
      if vid in registered_vendor_ids.keys():
        # TODO check registered_vendor_ids[vid] against name table values
        msg = "OS/2 VendorID is '{}' and registered to '{}'. Is that you?".format(vid, registered_vendor_ids[vid])
        logging.info(msg)
      elif vid.lower() in [item.lower() for item in registered_vendor_ids.keys()]:
        msg = "OS/2 VendorID '{}' is registered with different casing. You should check the case.".format(vid)
        logging.error(msg)
      else:
        msg = "OS/2 VendorID '{}' is not registered with Microsoft. You should register it at https://www.microsoft.com/typography/links/vendorlist.aspx".format(vid)
        logging.warning(msg)
    else:
      msg = "OS/2 VendorID '{}' could not be checked against Microsoft's list. You should check your internet connection and try again.".format(vid)
      logging.error(msg)
    bad_vids = ['UKWN', 'ukwn']
    if vid in bad_vids:
      logging.error("OS/2 VendorID is '{}'. You should set it to your own 4 character code, and register that code with Microsoft at https://www.microsoft.com/typography/links/vendorlist.aspx".format(vid))
    elif vid is None:
      logging.error("OS/2 VendorID is not set. You should set it.")
    else:
      logging.info("OK: OS/2 VendorID is '{}'".format(vid))

    #----------------------------------------------------
    logging.debug("Checking OS/2 usWeightClass")
    file_path, filename = os.path.split(font_file)
    filename_base, filename_extention = os.path.splitext(filename)
    family, style = filename_base.split('-')
    weight_class = font['OS/2'].usWeightClass
    # FIXME There has got to be a smarter way than these 4 lines, but they work
    weight_name = style
    if style.endswith("Italic"): 
      weight_name = style.replace("Italic","")
    if weight_name == "": 
      weight = "Italic"
    weights = {"Thin": 250, 
                "ExtraLight": 275,
                "Light": 300,
                "Regular": 400,
                "Italic": 400,
                "Medium": 500,
                "SemiBold": 600,
                "Bold": 700,
                "ExtraBold": 800,
                "Black": 900
               }
    if weight_class != weights[weight_name]:
      msg = "{} usWeightClass is {}".format(style, weight_class)
      logging.error(msg)
      font['OS/2'].usWeightClass = weights[weight_name]
      msg = "HOTFIX: {} usWeightClass is now {}".format(style, weights[weight_name])
      logging.info(msg)
    else:
      msg = "{} usWeightClass is {}".format(style, weight_class)
      logging.info(msg)
      
    #----------------------------------------------------
    logging.info("TODO: Check fsSelection")

    #----------------------------------------------------
    logging.info("TODO: Check head table")

    #----------------------------------------------------
    logging.info("TODO: Check name table")
    
    #----------------------------------------------------
    logging.debug("Checking name table for items without platformID=1")
    new_names = []
    non_pid1 = False
    for name in font['name'].names:
      if name.platformID != 1 and name.nameID not in [0, 1, 2, 3, 4, 5, 6, 18]:
        non_pid1 = True
        new_names.append(name)
    if non_pid1:
      font['name'].names = new_names
      logging.info("HOTFIX: name table items with platformID=1 were removed")
    else:
      logging.info("OK: name table has no records with platformID=1")

    #----------------------------------------------------
    logging.debug("TODO: Checking monospace aspects")
    # There are 2 tables in the OpenType spec that specify whether 
    # or not a font is monospaced. When a font is monospaced, the 
    # follow conditions must be met:
    # 
    # * Explicitely, the isFixedWidth value in the "post" table is set to 0
    # * Implicitely, the advanceWidthMax value in the "hhea" table 
    #      must be equal to each glyph's advanceWidth value
    # A fixer must check the advanceWidth values of all glyphs and 
    # if 90% of glyphs have the same width, it is truly a monospace.
    # Then 
    # * ['post'].isFixedWidth shoudl be set
    # * advanceWidthMax on "hhea" table should match
    # * panose monospace value hsould be set
    # * any glyphs not with that width should be an error
    # also if the glyphs are less than 90% the same width,
    # these thigns should NOT be set (sometimes they mistakenly are)

    #----------------------------------------------------
    logging.debug("Checking with ot-sanitise")
    try:
      ots_output = subprocess.check_output(["ot-sanitise", font_file], stderr=subprocess.STDOUT)
      if ots_output != "":
        logging.error("ot-sanitise output follows:\n\n{}\n".format(ots_output))
      else:
        logging.info("OK: ot-sanitise passed this file.")
    except OSError:
      logging.warning("ot-santise is not available. Install it, see https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md#ots")
      pass

    #----------------------------------------------------
    # more checks go here


    #----------------------------------------------------
    # TODO each fix line should set a fix flag, and 
    # if that flag is True by this point, only then write the file
    # and then re-run OTS as above
    font_file_output = '{}.fix'.format(font_file)
    font.save(font_file_output)
    font.close()
    logging.info("{} saved\n".format(font_file_output))

if __name__=='__main__':
    main()