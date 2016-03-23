#!/usr/bin/env python2

__author__="The Font Bakery Authors"

import os, sys, argparse, glob, logging, requests, subprocess
from bs4 import BeautifulSoup

from fontTools import ttLib

font = None
fixes = []
def assert_table_entry(tableName, fieldName, expectedValue, bitmask=None):
    """ This is a helper function to accumulate
    all fixes that a test performs so that we can
    print them all in a single line by invoking
    the log_results() function.

    Usage example:
    assert_table_entry('post', 'isFixedPitch', 1)
    assert_table_entry('OS/2', 'fsType', 0)
    log_results("Something test.")
    """

    #This is meant to support multi-level field hierarchy
    fields = fieldName.split('.')
    obj = font[tableName]
    for f in range(len(fields)-1):
        obj = getattr(obj, fields[f])
    field = fields[-1]
    value = getattr(obj, field)

    if bitmask==None:
        if value != expectedValue:
            setattr(obj, field, expectedValue)
            fixes.append("{} {} from {} to {}".format(tableName,
                                                      fieldName,
                                                      value,
                                                      expectedValue))
    else:
        if value & bitmask != expectedValue:
            expectedValue = (value & (~bitmask)) | expectedValue
            setattr(obj, field, expectedValue)
            fixes.append("{} {} from {} to {}".format(tableName,
                                                      fieldName,
                                                      value,
                                                      expectedValue))
            #TODO: Aestethical improvement:
            #      Create a helper function to format binary values
            #      highlighting the bits that are selected by a bitmask

def log_results(message):
    """ Concatenate all fixes that happened up to now
    in a good and regular syntax """
    global fixes
    if fixes == []:
        logging.info("OK: " + message)
    else:
        logging.error("HOTFIXED: {} Fixes: {}".format(message,
                                                      " | ".join(fixes)))
        # empty the buffer of fixes,
        # in preparation for the next test
        fixes = []

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
      mimetype = mime.from_file(fullpath)
      if mimetype == 'application/x-font-ttf':
        logging.debug("'{}' has a ttf mimetype".format(file_name))
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping '{}' as mime was '{}', should be 'application/x-font-ttf')".format(filename, mimetype))
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
    filename_base, filename_extension = os.path.splitext(filename)
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
    assert_table_entry('OS/2', 'fsType', 0)
    log_results("fsType is zero.")

    #----------------------------------------------------
    logging.debug("Checking OS/2 achVendID")
    vid = font['OS/2'].achVendID
    bad_vids = ['UKWN', 'ukwn', 'PfEd']
    if vid is None:
      logging.error("OS/2 VendorID is not set. You should set it to your own 4 character code, and register that code with Microsoft at https://www.microsoft.com/typography/links/vendorlist.aspx")
    elif vid in bad_vids:
      logging.error("OS/2 VendorID is '{}', a font editor default. You should set it to your own 4 character code, and register that code with Microsoft at https://www.microsoft.com/typography/links/vendorlist.aspx".format(vid))
    elif len(registered_vendor_ids.keys()) > 0:
      if vid in registered_vendor_ids.keys():
        # TODO check registered_vendor_ids[vid] against name table values
        msg = "OK: OS/2 VendorID is '{}' and registered to '{}'. Is that legit?".format(vid, registered_vendor_ids[vid])
        logging.info(msg)
      elif vid.lower() in [item.lower() for item in registered_vendor_ids.keys()]:
        msg = "OS/2 VendorID is '{}' but this is registered with different casing. You should check the case.".format(vid)
        logging.error(msg)
      else:
        msg = "OS/2 VendorID is '{}' but this is not registered with Microsoft. You should register it at https://www.microsoft.com/typography/links/vendorlist.aspx".format(vid)
        logging.warning(msg)
    else:
      msg = "OK: OS/2 VendorID is '{}' but could not be checked against Microsoft's list. You should check your internet connection and try again.".format(vid)

    #----------------------------------------------------
    # fsSelection bit definitions:
    FSSEL_ITALIC         = (1 << 0)
    FSSEL_UNDERSCORE     = (1 << 1)
    FSSEL_NEGATIVE       = (1 << 2)
    FSSEL_OUTLINED       = (1 << 3)
    FSSEL_STRIKEOUT      = (1 << 4)
    FSSEL_BOLD           = (1 << 5)
    FSSEL_REGULAR        = (1 << 6)
    FSSEL_USETYPOMETRICS = (1 << 7)
    FSSEL_WWS            = (1 << 8)
    FSSEL_OBLIQUE        = (1 << 9)

    # macStyle bit definitions:
    MACSTYLE_BOLD   = (1 << 0)
    MACSTYLE_ITALIC = (1 << 1)

    # weight name to value mapping:
    WEIGHTS = {"Thin": 250,
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

    # Panose definitions:
    PANOSE_PROPORTION_ANY = 0
    PANOSE_PROPORTION_NO_FIT = 1
    PANOSE_PROPORTION_OLD_STYLE = 2
    PANOSE_PROPORTION_MODERN = 3
    PANOSE_PROPORTION_EVEN_WIDTH = 4
    PANOSE_PROPORTION_EXTENDED = 5
    PANOSE_PROPORTION_CONDENSED = 6
    PANOSE_PROPORTION_VERY_EXTENDED = 7
    PANOSE_PROPORTION_VERY_CONDENSED = 8
    PANOSE_PROPORTION_MONOSPACED = 9

    #----------------------------------------------------
    file_path, filename = os.path.split(font_file)
    family, style = os.path.splitext(filename)[0].split('-')
    if style.endswith("Italic") and style != "Italic":
        weight_name = style.replace("Italic","")
    else:
        weight_name = style

    #----------------------------------------------------
    logging.debug("Checking OS/2 usWeightClass")
    assert_table_entry('OS/2', 'usWeightClass', WEIGHTS[weight_name])
    log_results("OS/2 usWeightClass")

    #----------------------------------------------------
    logging.debug("Checking fsSelection REGULAR bit")
    expected = 0
    if "Regular" in style:
        expected = FSSEL_REGULAR
    assert_table_entry('OS/2', 'fsSelection', expected, bitmask=FSSEL_REGULAR)
    log_results("fsSelection REGULAR bit")

    #----------------------------------------------------
    logging.debug("Checking that italicAngle <= 0")

    value = font['post'].italicAngle
    if value > 0:
        font['post'].italicAngle = -value
        logging.error("HOTFIXED: italicAngle from {} to {}".format(value, -value))
    else:
        logging.info("OK: italicAngle <= 0")
    #----------------------------------------------------
    logging.debug("Checking if italicAngle matches font style")

    if "Italic" in style:
       if font['post'].italicAngle == 0:
           logging.error("Font is italic, so italicAngle should be non-zero.")
       else:
           loggin.info("OK: italicAngle matches font style")
    else:
       assert_table_entry('post', 'italicAngle', 0)
       log_results("matching of fontstyle and italicAngle value")

    #----------------------------------------------------
    #TODO: checker for proper italic names in name table

    #----------------------------------------------------
    logging.debug("Checking fsSelection ITALIC bit")
    expected = 0
    if "Italic" in style:
        expected = FSSEL_ITALIC
    assert_table_entry('OS/2', 'fsSelection', expected, bitmask=FSSEL_ITALIC)
    log_results("fsSelection ITALIC bit")

    #----------------------------------------------------
    logging.debug("Checking macStyle ITALIC bit")
    expected = 0
    if "Italic" in style:
        expected = MACSTYLE_ITALIC
    assert_table_entry('head', 'macStyle', expected, bitmask=FSSEL_ITALIC)
    log_results("macStyle ITALIC bit")

    #----------------------------------------------------
    logging.debug("Checking fsSelection BOLD bit")
    expected = 0
    if style in ["Bold", "BoldItalic"]:
        expected = FSSEL_BOLD
    assert_table_entry('OS/2', 'fsSelection', expected, bitmask=FSSEL_BOLD)
    log_results("fsSelection BOLD bit")

    #----------------------------------------------------
    logging.debug("Checking macStyle BOLD bit")
    expected = 0
    if style in ["Bold", "BoldItalic"]:
        expected = MACSTYLE_BOLD
    assert_table_entry('head', 'macStyle', expected, bitmask=MACSTYLE_BOLD)
    log_results("macStyle BOLD bit")

    #----------------------------------------------------
    logging.debug("TODO: Check name table")
    # TODO: Check that OFL.txt or LICENSE.txt exists in the same directory as font_file, if not then warn that there should be one. If exists, then check its first line matches the copyright namerecord, and that each namerecord is identical
    # TODO Check license and license URL are correct, hotfix them if not
    # TODO Check namerecord 9 ("description") is not there, drop it if so
    
    
    #----------------------------------------------------
    logging.debug("Checking name table for items without platformID=1")
    new_names = []
    changed = False
    for name in font['name'].names:
      if name.platformID != 1 and name.nameID not in [0, 1, 2, 3, 4, 5, 6, 18]\
         or name.platformID == 1 and name.nameID in [1,2,4,6]: #see https://github.com/googlefonts/fontbakery/issues/649
        new_names.append(name)
      else:
        changed = True
    if changed:
      font['name'].names = new_names
      logging.error("HOTFIXED: some name table items with platformID=1 were removed")
    else:
      logging.info("OK: name table has only the bare-minimum records with platformID=1")

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
    # * OS/2.panose.bProportion must be set to 9 (monospace). Spec says:
    #   "The PANOSE definition contains ten digits each of which currently
    #   describes up to sixteen variations. Windows uses bFamilyType,
    #   bSerifStyle and bProportion in the font mapper to determine 
    #   family type. It also uses bProportion to determine if the font 
    #   is monospaced." 
    #   www.microsoft.com/typography/otspec/os2.htm#pan
    #   monotypecom-test.monotype.de/services/pan2
    #
    # * OS/2.xAverageWidth must be set accurately. 
    #   "OS/2.xAverageWidth IS used when rendering monospaced fonts, 
    #   at least by Windows GDI"
    #   http://typedrawers.com/discussion/comment/15397/#Comment_15397
    #
    # Also we should report an error for glyphs not of average width
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
        # spec says post.isFixedPitch non-zero value means monospaced
        assert_table_entry('post', 'isFixedPitch', 1)
        assert_table_entry('hhea', 'advanceWidthMax', width_max)
        assert_table_entry('OS/2', 'panose.bProportion', PANOSE_PROPORTION_MONOSPACED)
        assert_table_entry('OS/2', 'xAvgCharWidth', width_max) #FIXME: Felipe: This needs to be discussed with Dave
        # TODO 
        # If any glyphs are outliers, note them
        outliers = len(glyphs) - occurrences
        # FIXME this if/else should be swapped, so the if evaluates the condition we look for, and else handles the OK case
        if outliers == 0:
            log_results("Font is monospaced.")
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
        # FIXME set panose value to anything except 9
        assert_table_entry('OS/2', 'panose.bProportion', PANOSE_PROPORTION_ANY) #FIXEME: Dave, is it the correct value here?
        assert_table_entry('OS/2', 'xAvgCharWidth', width_max) #FIXME: Felipe: This needs to be discussed with Dave
        log_results("Font is not monospaced.")

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
    # fontbakery-check-ttf.py ~/fonts/apache/cousine/Cousine-Regular.ttf 
    #   The following table(s) in the font have been ignored by FontForge
    #     Ignoring 'VDMX' vertical device metrics table
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
    font.save(font_file_output)
    font.close()
    logging.info("{} saved\n".format(font_file_output))

if __name__=='__main__':
    main()
