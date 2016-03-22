#!/usr/bin/env python2

__author__="The Font Bakery Authors"

import os, sys, argparse, glob, logging, requests, subprocess
from bs4 import BeautifulSoup

from fontTools import ttLib

font = None
fixes = []
def assert_table_entry(tableName, fieldName, expectedValue):
    """ This is a helper function to accumulate
    all fixes that a test performs so that we can
    print them all in a single line by invoking
    the fixes_str() function.

    Usage example:
    assert_table_entry('post', 'isFixedPitch', 1)
    assert_table_entry('OS/2', 'fsType', 0)
    logger.info("Something test " + fixes_str())
    """

    value = getattr(font[tableName], fieldName)
    if value != expectedValue:
        setattr(font[tableName], fieldName, expectedValue)
        fixes.append("{} {} from {} to {}".format(tableName, 
                                                  fieldName,
                                                  value,
                                                  expectedValue))

def fixes_str():
    """ Concatenate all fixes that happened up to now
    in a good and regular syntax """
    global fixes
    if fixes == []:
        return ""
    fixes_log_message = "HOTFIXED: " + " | ".join(fixes)
    # empty the buffer of fixes,
    # in preparation for the next test
    fixes = []

    return fixes_log_message

def main():
  # set up a basic logging config
  # to include timestamps
  # log_format = '%(asctime)s %(levelname)-8s %(message)s'
  global font
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
  parser.add_argument('arg_filepaths', nargs='+', 
    help='font file path(s) to check. Wildcards like *.ttf are allowed.')
  args = parser.parse_args()

  #------------------------------------------------------
  import magic
  logging.debug("Checking each file is a ttf")
  fonts_to_check = []
  for arg_filepath in sorted(args.arg_filepaths):
    # use glob.glob to accept *.ttf
    for fullpath in glob.glob(arg_filepath):
      file_path, file_name = os.path.split(fullpath)
      mime = magic.Magic(mime=True)
      if mime.from_file(fullpath) == 'application/font-ttf':
        logging.debug("{} has a ttf mimetype".format(file_name))
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping {}".format(file_name))
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
    # remove spaces in style names
    style_file_names = [name.replace(' ', '') for name in style_names]
    try: 
      family, style = filename_base.split('-')
      if style in style_file_names:
        logging.info("OK: {} is named canonically".format(font_file))
      else:
        logging.critical("{} is named Family-Style.ttf but Style is not canonical. You should rebuild it with a canonical style name".format(font_file))
        not_canonical.append(font_file)
    except:
        logging.critical("{} is not named canonically, as Family-Style.ttf".format(font_file))
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
        # pad the code to make sure it is a 4 char string,
        # otherwise eg "CF  " will not be matched to "CF"
        code = cells[0].string.strip()
        code = code + (4 - len(code)) * ' '
        labels = [label for label in cells[1].stripped_strings]
        registered_vendor_ids[code] = labels[0]
    except:
      logging.warning("Failed to parse Microsoft's vendorID list.")
  except:
    logging.warning("Failed to fetch Microsoft's vendorID list.")

  #------------------------------------------------------
  for font_file in fonts_to_check:
    font = ttLib.TTFont(font_file)
    logging.info("OK: {} opened with fontTools".format(font_file))
    
    #----------------------------------------------------
    # OS/2 fsType is a legacy DRM-related field from the 80's
    # It should be disabled in all fonts.
    logging.debug("Checking OS/2 fsType")
    assert_table_value('OS/2', 'fsType', 0)
    logging.info("OK: fsType is 0. " + fixes_str())

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
    bad_vids = ['UKWN', 'ukwn', 'PfEd']
    if vid in bad_vids:
      logging.error("OS/2 VendorID is '{}', a font editor default. You should set it to your own 4 character code, and register that code with Microsoft at https://www.microsoft.com/typography/links/vendorlist.aspx".format(vid))
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
      # FIXME add checks for fsSelection, italicAngle
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
    if weight_name == "Regular":
      # FIXME add checks for fsSelection
      pass
    elif weight_name == "Bold":
      # FIXME add checks for macStyle, fsSelection
      pass
    else:
      # FIXME add checks for macStyle, fsSelection NOT set
      pass

    if weight_class != weights[weight_name]:
      msg = "{} usWeightClass is {}".format(style, weight_class)
      logging.error(msg)
      font['OS/2'].usWeightClass = weights[weight_name]
      msg = "HOTFIX: {} usWeightClass is now {}".format(style, weights[weight_name])
      logging.info(msg)
    else:
      msg = "OK: {} usWeightClass is {}".format(style, weight_class)
      logging.info(msg)
      
    #----------------------------------------------------
    logging.info("TODO: Check fsSelection")

    #----------------------------------------------------
    logging.info("TODO: Check head table")

    #----------------------------------------------------
    logging.info("TODO: Check name table")
    # TODO: Check that OFL.txt or LICENSE.txt exists in the same directory as font_file, if not then warn that there should be one. If exists, then check its first line matches the copyright namerecord, and that each namerecord is identical
    # TODO Check license and license URL are correct, hotfix them if not
    # TODO Check namerecord 9 ("description") is not there, drop it if so
    
    
    #----------------------------------------------------
    # TODO this needs work, see https://github.com/behdad/fonttools/issues/146#issuecomment-176761350 and https://github.com/googlefonts/fontbakery/issues/631
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
    # There are various metadata in the OpenType spec to specify if 
    # a font is monospaced or not. 
    #
    # The source of truth for if a font is monospaced is if 90% of all
    # glyphs have the same width. If this is true then these metadata
    # must be set.
    # 
    # If not true, no monospaced metadata should be set (as sometimes 
    # they mistakenly are...)
    #
    # Monospace fonts must:
    #
    # * post.isFixedWidth "Set to 0 if the font is proportionally spaced,
    #   non-zero if the font is not proportionally spaced (monospaced)"  
    #   www.microsoft.com/typography/otspec/post.htm
    #
    # * hhea.advanceWidthMax must be correct, meaning no glyph's 
    #   width value is greater.
    #   www.microsoft.com/typography/otspec/hhea.htm
    #
    # * panose monospace value must be set. Spec says:
    #   "The PANOSE definition contains ten digits each of which currently
    #   describes up to sixteen variations. Windows uses bFamilyType,
    #   bSerifStyle and bProportion in the font mapper to determine 
    #   family type. It also uses bProportion to determine if the font 
    #   is monospaced." 
    #   www.microsoft.com/typography/otspec/os2.htm#pan
    #   monotypecom-test.monotype.de/services/pan2
    #
    # Also we should report an error for glyphs not of typical width
    logging.debug("Checking if the font is truly monospaced")
    glyphs = font['glyf'].glyphs
    width_occurrences = {}
    width_max = 0
    # count how many times a width occurs
    for glyph_id in glyphs:
        width = font['hmtx'].metrics[glyph_id][0]
        width_max = max(width, width_max)
        try:
            width_occurrences[width] += 1
        except KeyError:
            width_occurrences[width] = 1
    # find the most_common_width
    occurrences = 0
    for width in width_occurrences.keys():
        if width_occurrences[width] > occurrences:
            occurrences = width_occurrences[width]
            most_common_width = width
    # if more than 90% of glyphs have the same width, set monospaced metadata
    monospace_detected = occurrences > 0.90 * len(glyphs)
    if monospace_detected:
        # TODO confirm that the previous values for these 3 are correct
        # spec says post.isFixedPitch non-zero value means monospaced
        assert_table_entry('post', 'isFixedPitch', 1)
        assert_table_entry('hhea', 'advanceWidthMax', width_max)
        assert_table_entry('OS/2', 'panose.bProportion', 9)
        # If any glyphs are outliers, note them
        outliers = len(glyphs) - occurrences
        # FIXME this if/else should be swapped, so the if evaluates the condition we look for, and else handles the OK case
        if outliers == 0:
            logging.info("OK: Font is monospaced. " + fixes_str())
        else:
            unusually_spaced_glyphs = [g for g in glyphs if font['hmtx'].metrics[g][0] != most_common_width]
            # FIXME strip glyphs named .notdef .null etc from the unusually_spaced_glyphs list
            logging.warn("Font is monospaced but {} glyphs have a different width.".format(outliers) +\
                         " You should check the widths of: {}".format(unusually_spaced_glyphs))
    # else it is not monospaced, so unset monospaced metadata
    else:
        # spec says post.isFixedPitch zero value means monospaced
        assert_table_entry('post', 'isFixedPitch', 0)
        assert_table_entry('hhea', 'advanceWidthMax', width_max)
        # FIXME set panose value here
        logging.info("OK: Font is not monospaced. " + fixes_str())

    #----------------------------------------------------
    logging.debug("Checking with ot-sanitise")
    try:
      ots_output = subprocess.check_output(["ot-sanitise", font_file], stderr=subprocess.STDOUT)
      if ots_output != "":
        logging.error("ot-sanitise output follows:\n\n{}\n".format(ots_output))
      else:
        logging.info("OK: ot-sanitise passed this file")
    except OSError:
      logging.warning("ot-santise is not available. Install it, see https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md#ots")
      pass

    #----------------------------------------------------
    # TODO FontForge will sometimes say stuff on STDERR like
    #
    #   The glyph named circumflex is mapped to U+F031F.
    #   But its name indicates it should be mapped to U+02C6.
    #
    # We should detect this and if found, warn with it
    logging.debug("Checking with fontforge")
    try:
        import fontforge
    except ImportError:
        logging.warning("fontforge python module is not available. Install it, see https://github.com/googlefonts/gf-docs/blob/master/ProjectChecklist.md#fontforge")
        pass
    try:
      fontforge_font = fontforge.open(font_file)
      # TODO: port fontforge validation check from 0.0.15 to here
    except:
      logging.warning('fontforge python module could not open {}'.format(font_file))

    #----------------------------------------------------
    # more checks go here

    #------------------------------------------------------
    # TODO Run pyfontaine checks for subset coverage, using the thresholds in add_font.py. See https://github.com/googlefonts/fontbakery/issues/594

    #----------------------------------------------------    
    # TODO check for required tables, was test_check_no_problematic_formats(). See https://github.com/googlefonts/fontbakery/issues/617

    #----------------------------------------------------
    # TODO Fonts have old ttfautohint applied, so port 
    # fontbakery-fix-version.py here and:
    #
    # 1. find which version was used, grepping the name table or reading the ttfa table (which are created if the `-I` or `-t` args respectively were passed to ttfautohint, to record its args in the ttf file) (there is a pypi package https://pypi.python.org/pypi/font-ttfa for reading the ttfa table, although per https://github.com/source-foundry/font-ttfa/issues/1 it might be better to inline the code... :) 
    #
    # 2. find which version of ttfautohint is installed (and warn if not available, similar to ots check above
    #
    # 3. rehint the font with the latest version of ttfautohint using the same options

    #----------------------------------------------------
    # TODO each fix line should set a fix flag, and 
    # if that flag is True by this point, only then write the file
    # and then say any further output regards fixed files, and 
    # re-run the script on each fixed file with logging level = error
    # so no info-level log items are shown
    font_file_output = font_file.replace('ttf','fix')
    os.path.join(directory
    font.save(font_file_output)
    font.close()
    logging.info("{} saved\n".format(font_file_output))

if __name__=='__main__':
    main()
