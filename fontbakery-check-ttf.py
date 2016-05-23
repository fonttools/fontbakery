#!/usr/bin/env python2
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
__author__="The Font Bakery Authors"

import os
import sys
import argparse
import glob
import logging
import subprocess
import requests
import urllib
import csv
import re
from bs4 import BeautifulSoup
from fontTools import ttLib
from fontTools.ttLib.tables._n_a_m_e import NameRecord

try:
  from google.protobuf import text_format
except:
  sys.exit("Needs protobuf.\n\nsudo pip install protobuf")

from fonts_public_pb2 import FontProto, FamilyProto

#=====================================
# GLOBAL CONSTANTS DEFINITIONS

PROFILES_GIT_URL = 'https://github.com/google/fonts/blob/master/designers/profiles.csv'
PROFILES_RAW_URL = 'https://raw.githubusercontent.com/google/fonts/master/designers/profiles.csv'

STYLE_NAMES = ["Thin",
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

# Weight name to value mapping:
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

# nameID definitions for the name table:
NAMEID_COPYRIGHT_NOTICE = 0
NAMEID_FONT_FAMILY_NAME = 1
NAMEID_FONT_SUBFAMILY_NAME = 2
NAMEID_UNIQUE_FONT_IDENTIFIER = 3
NAMEID_FULL_FONT_NAME = 4
NAMEID_VERSION_STRING = 5
NAMEID_POSTSCRIPT_NAME = 6
NAMEID_TRADEMARK = 7
NAMEID_MANUFACTURER_NAME = 8
NAMEID_DESIGNER = 9
NAMEID_DESCRIPTION = 10
NAMEID_VENDOR_URL = 11
NAMEID_DESIGNER_URL = 12
NAMEID_LICENSE_DESCRIPTION = 13
NAMEID_LICENSE_INFO_URL = 14
# Name ID 15 is RESERVED
NAMEID_TYPOGRAPHIC_FAMILY_NAME = 16
NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME = 17
NAMEID_COMPATIBLE_FULL_MACONLY = 18
NAMEID_SAMPLE_TEXT = 19
NAMEID_POSTSCRIPT_CID_NAME = 20
NAMEID_WWS_FAMILY_NAME = 21
NAMEID_WWS_SUBFAMILY_NAME = 22
NAMEID_LIGHT_BACKGROUND_PALETTE = 23
NAMEID_DARK_BACKGROUD_PALETTE = 24

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

# 'post' table / isFixedWidth definitions:
IS_FIXED_WIDTH_NOT_MONOSPACED = 0
IS_FIXED_WIDTH_MONOSPACED = 1 # any non-zero value means monospaced

PLATFORM_ID_UNICODE = 0
PLATFORM_ID_MACHINTOSH = 1
PLATFORM_ID_ISO = 2
PLATFORM_ID_WINDOWS = 3
PLATFORM_ID_CUSTOM = 4

PLAT_ENC_ID_UCS2 = 1
LANG_ID_ENGLISH_USA = 0x0409

PLACEHOLDER_LICENSING_TEXT = {
    'OFL.txt': 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at http://scripts.sil.org/OFL',
    'LICENSE.txt': 'This Font Software is licensed under the Apache License, Version 2.0. This license is available with a FAQ at www.apache.org/foundation/license-faq.html'
}

REQUIRED_TABLES = set(['cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name',
                       'OS/2', 'post'])
OPTIONAL_TABLES = set(['cvt', 'fpgm', 'loca', 'prep',
                       'VORG', 'EBDT', 'EBLC', 'EBSC', 'BASE', 'GPOS',
                       'GSUB', 'JSTF', 'DSIG', 'gasp', 'hdmx', 'kern',
                       'LTSH', 'PCLT', 'VDMX', 'vhea', 'vmtx'])

#=====================================
# HELPER FUNCTIONS

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
        if (value & bitmask) != expectedValue:
            expectedValue = (value & (~bitmask)) | expectedValue
            setattr(obj, field, expectedValue)
            fixes.append("{} {} from {} to {}".format(tableName,
                                                      fieldName,
                                                      value,
                                                      expectedValue))
            #TODO: Aestethical improvement:
            #      Create a helper function to format binary values
            #      highlighting the bits that are selected by a bitmask

def log_results(message, hotfix=True):
    """ Concatenate and log all fixes that happened up to now
    in a good and regular syntax """
    global fixes
    if fixes == []:
        logging.info("OK: " + message)
    else:
        if hotfix:
            msg = "HOTFIXED: {} Fixes: {}"
        else:
            msg = "CRITICAL FAILURE: {} {}"
        logging.error(msg.format(message,
                                 " | ".join(fixes)))
        # empty the buffer of fixes,
        # in preparation for the next test
        fixes = []

# Maybe fonttools should provide us a helper method like this one...
#TODO: verify if fonttools doesn't really provide that and then
#      possibily contribute something equivalent to this upstream.
def makeNameRecord(text, nameID, platformID, platEncID, langID):
    """ Helper function to create a new NameRecord entry """
    name = NameRecord()
    name.nameID, name.platformID, name.platEncID, name.langID = (
        nameID, platformID, platEncID, langID)
    name.string = text.encode(name.getEncoding())
    return name

def get_bounding_box(font):
    """ Returns max and min bbox of given truetype font """
    ymin = 0
    ymax = 0
    if font.sfntVersion == 'OTTO':
        ymin = font['head'].yMin
        ymax = font['head'].yMax
    else:
        for g in font['glyf'].glyphs:
            char = font['glyf'][g]
            if hasattr(char, 'yMin') and ymin > char.yMin:
                ymin = char.yMin
            if hasattr(char, 'yMax') and ymax < char.yMax:
                ymax = char.yMax
    return ymin, ymax

def get_name_string(font, nameID):
    for entry in font['name'].names:
        if entry.nameID == nameID:
            return entry.string.decode(entry.getEncoding())
    return False

def parse_version_string(s):
    """ Tries to parse a version string as used
        in ttf versioning metadata fields.
        Example of expected format is:
          'Version 01.003; Comments'
    """
    try:
        suffix = ''
        if ';' in s:
            fields = s.split(';')
            s = fields[0]
            fields.pop(0)
            suffix = ';'.join(fields)
        substrings = s.split('.')
        minor = substrings[-1]
        if ' ' in substrings[-2]:
            major = int(substrings[-2].split(' ')[-1])
        else:
            major = int(substrings[-2])
        return major, minor, suffix
    except:
        logging.error("Failed to detect major and minor version numbers" +\
               " in '{}' utf8 encoding: {}".format(s, [s.encode('utf8')]))

def getGlyph(font, uchar):
    for table in font['cmap'].tables:
        if not (table.platformID == 3 and table.platEncID in [1, 10]):
            continue
        if uchar in table.cmap:
            return table.cmap[uchar]
    return None

def addGlyph(font, uchar, glyph):
    # Add to glyph list
    glyphOrder = font.getGlyphOrder()
    # assert glyph not in glyphOrder
    glyphOrder.append(glyph)
    font.setGlyphOrder(glyphOrder)

    # Add horizontal metrics (to zero)
    font['hmtx'][glyph] = [0, 0]

    # Add to cmap
    for table in font['cmap'].tables:
        if not (table.platformID == 3 and table.platEncID in [1, 10]):
            continue
        if not table.cmap:  # Skip UVS cmaps
            continue
        assert uchar not in table.cmap
        table.cmap[uchar] = glyph

    # Add empty glyph outline
    if 'glyf' in font:
        font['glyf'].glyphs[glyph] = ttLib.getTableModule('glyf').Glyph()
    else:
        cff = font['CFF '].cff
        self.addCFFGlyph(
            glyphName=glyph,
            private=cff.topDictIndex[0].Private,
            globalSubrs=cff.GlobalSubrs,
            charStringsIndex=cff.topDictIndex[0].CharStrings.charStringsIndex,
            # charStringsIndex=cff.topDictIndex[0].CharStrings.charStrings.charStringsIndex,
            topDict=cff.topDictIndex[0],
            charStrings=cff.topDictIndex[0].CharStrings
        )
        import ipdb; ipdb.set_trace()
    return glyph

def getWidth(font, glyph):
    return font['hmtx'][glyph][0]

def setWidth(font, glyph, width):
    font['hmtx'][glyph] = (width, font['hmtx'][glyph][1])

def glyphHasInk(font, name):
    """Checks if specified glyph has any ink.
    That is, that it has at least one defined contour associated. Composites are
    considered to have ink if any of their components have ink.
    Args:
        font:       the font
        glyph_name: The name of the glyph to check for ink.
    Returns:
        True if the font has at least one contour associated with it.
    """
    glyph = font['glyf'].glyphs[name]
    glyph.expand(font['glyf'])
    if not glyph.isComposite():
        if glyph.numberOfContours == 0:
            return False
        (coords, _, _) = glyph.getCoordinates(font['glyf'])
        # you need at least 3 points to draw
        return len(coords) > 2

    # composite is blank if composed of blanks
    # if you setup a font with cycles you are just a bad person
    for glyph_name in glyph.getComponentNames(glyph.components):
        if glyphHasInk(font, glyph_name):
            return True
    return False

def get_FamilyProto_Message(path):
    message = FamilyProto()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, message)
    return message

#=====================================
# Main sequence of checkers & fixers

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
  # set up some command line argument processing
  parser = argparse.ArgumentParser(description="Check TTF files for common issues.")
  parser.add_argument('arg_filepaths', nargs='+', 
    help='font file path(s) to check. Wildcards like *.ttf are allowed.')
  parser.add_argument('-v', '--verbose', action='count', default=0)
  args = parser.parse_args()
  if args.verbose == 1:
    logger.setLevel(logging.INFO)
  elif args.verbose >= 2:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.ERROR)

  #------------------------------------------------------
  logging.debug("Checking each file is a ttf")
  fonts_to_check = []
  for arg_filepath in sorted(args.arg_filepaths):
    # use glob.glob to accept *.ttf
    for fullpath in glob.glob(arg_filepath):
      file_path, file_name = os.path.split(fullpath)
      if file_name.endswith(".ttf"):
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping '{}' as it does not seem to be valid TrueType font file')".format(file_name))
  fonts_to_check.sort()

  if fonts_to_check == []:
    logging.error("None of the fonts are valid TrueType files!")

  #------------------------------------------------------
  logging.debug("Checking files are named canonically")
  not_canonical = []

  for font_file in fonts_to_check:
    file_path, filename = os.path.split(font_file)
    filename_base, filename_extension = os.path.splitext(filename)
    # remove spaces in style names
    style_file_names = [name.replace(' ', '') for name in STYLE_NAMES]
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
  logging.debug("Fetching Microsoft's vendorID list")
  url = 'https://www.microsoft.com/typography/links/vendorlist.aspx'
  registered_vendor_ids = {}
  try:
    import tempfile
    CACHE_VENDOR_LIST = os.path.join(tempfile.gettempdir(), 'fontbakery-microsoft-vendorlist.cache')
    if os.path.exists(CACHE_VENDOR_LIST):
      content = open(CACHE_VENDOR_LIST).read()
    else:
      logging.error("Did not find cached vendor list at: " + CACHE_VENDOR_LIST)
      content = requests.get(url, auth=('user', 'pass')).content
      open(CACHE_VENDOR_LIST, 'w').write(content)
    soup = BeautifulSoup(content, 'html.parser')
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

###########################################################################
## Step 1: Cross-family tests
##         * Validates consistency of data throughout all TTF files
##           in a given family
##         * The list of TTF files in infered from the METADATA.pb file
##         * We avoid testing the same fmaily twice by deduplicating the
##           list of METADATA.pb files first
###########################################################################

  metadata_to_check = []
  for font_file in fonts_to_check:
    fontdir = os.path.dirname(font_file)
    metadata = os.path.join(fontdir, "METADATA.pb")
    if not os.path.exists(metadata):
      logging.error("{} is missing a METADATA.pb file!".format(file_path))
    else:
      family = get_FamilyProto_Message(metadata)
      if family not in metadata_to_check:
        metadata_to_check.append([fontdir, family])

  def ttf_file(f):
    simplehash = f.filename #this may collide. Perhaps we need something better here.
    return ttf[simplehash]

  for dirname, family in metadata_to_check:
    ttf = {}
    for f in family.fonts:
      if f.filename in ttf.keys():
        logging.error("This is a fontbakery bug. Please contact us. We may need to figure out a better hash-function for the font ProtocolBuffer message...")
      else:
        ttf[f.filename] = ttLib.TTFont(os.path.join(dirname, f.filename))

    #-----------------------------------------------------
    logging.debug("The same number of glyphs across family?")
    glyphs_count = 0
    fail = False
    for f in family.fonts:
      ttfont = ttf_file(f)
      if not glyphs_count:
        glyphs_count = len(ttfont['glyf'].glyphs)

      if glyphs_count != len(ttfont['glyf'].glyphs):
        fail = True

    if fail:
      logging.error('Family has a different glyphs\'s count in fonts')
    else:
      logging.info("OK: same number of glyphs across family.")
      
    #-----------------------------------------------------
    logging.debug("The same names of glyphs across family?")
    glyphs = None
    fail = False
    for f in family.fonts:
      ttfont = ttf_file(f)
      if not glyphs:
        glyphs = ttfont['glyf'].glyphs
    
      if glyphs != ttfont['glyf'].glyphs:
        fail = True

    if fail:
      logging.error('Family has a different glyphs\'s names in fonts')
    else:
      logging.info("OK: same names of glyphs across family.")
    
    #-----------------------------------------------------
    logging.debug("The same unicode encodings of glyphs across family?")
    encoding = None
    fail = False
    for f in family.fonts:
      ttfont = ttf_file(f)
      cmap = None
      for table in ttfont['cmap'].tables:
        if table.format == 4:
          cmap = table
          break

      if not encoding:
         encoding = cmap.platEncID
    
      if encoding != cmap.platEncID:
        fail=True

    if fail:
      logging.error('Family has different encoding across fonts')
    else:
      logging.info("OK: same unicode encodings of glyphs across family.")

###########################################################################
## Step 2: Single TTF tests
##         * Tests that only check data of the specific TTF file, but not 
##           the other fonts in the same family
###########################################################################
 #------------------------------------------------------
  vmetrics_ymin = 0
  vmetrics_ymax = 0
  for font_file in fonts_to_check:
    font = ttLib.TTFont(font_file)
    font_ymin, font_ymax = get_bounding_box(font)
    vmetrics_ymin = min(font_ymin, vmetrics_ymin)
    vmetrics_ymax = max(font_ymax, vmetrics_ymax)

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
        for name in font['name'].names:
          if name.nameID == NAMEID_MANUFACTURER_NAME:
            manufacturer = name.string.decode(name.getEncoding()).strip()
            if manufacturer != registered_vendor_ids[vid].strip():
              logging.warning("VendorID string '{}' does not match nameID 8 (Manufacturer Name): '{}'".format(\
                  registered_vendor_ids[vid].strip(), manufacturer))
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
      logging.warning(msg)

    #----------------------------------------------------
    logging.debug("substitute copyright, registered and trademark symbols in name table entries")
    new_names = []
    nametable_updated = False
    replacement_map = [(u"\u00a9", '(c)'), (u"\u00ae", '(r)'), (u"\u2122", '(tm)')]
    for name in font['name'].names:
        new_name = name
        original = name.string
        string = name.string
        for mark, ascii_repl in replacement_map:
            string = string.replace(mark, ascii_repl)
        new_name.string = string.encode(name.getEncoding())
        if string != original:
            logging.error("HOTFIXED: Name entry fixed to '{}'.".format(string))
            nametable_updated = True
        new_names.append(new_name)
    if nametable_updated:
        logging.error("HOTFIXED: Name table entries were modified to replace unicode symbols such as (c), (r) and TM.")
        font['name'].names = new_names

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
    logging.debug("Checking that italicAngle is less than 20 degrees")

    value = font['post'].italicAngle
    if abs(value) > 20:
        font['post'].italicAngle = -20
        logging.error("HOTFIXED: italicAngle from {} to -20 (italicAngle can\'t be larger than 20 degrees)".format(value))
    else:
        logging.info("OK: italicAngle is less than 20 degrees.")

    #----------------------------------------------------
    logging.debug("Checking if italicAngle matches font style")

    if "Italic" in style:
       if font['post'].italicAngle == 0:
           logging.error("Font is italic, so italicAngle should be non-zero.")
       else:
           logging.info("OK: italicAngle matches font style")
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
    assert_table_entry('head', 'macStyle', expected, bitmask=MACSTYLE_ITALIC)
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
    logging.debug("Check font has a license")
    # Check that OFL.txt or LICENSE.txt exists in the same
    # directory as font_file, if not then warn that there should be one.
    found = False
    for license in ['OFL.txt', 'LICENSE.txt']:
      license_path = os.path.join(file_path, license)
      if os.path.exists(license_path):
          if found != False:
             logger.error("More than a single license file found. Please review.")
             found = "multiple"
          else:
             found = license_path

    if found != "multiple":
        if found == False:
            logger.error("No license file was found. Please add an OFL.txt or a LICENSE.txt file.")
        else:
            logger.info("OK: Found license at '{}'".format(found))

    #----------------------------------------------------
    logging.debug("Check copyright namerecords match license file")
    new_names = []
    names_changed = False
    for license in ['OFL.txt', 'LICENSE.txt']:
        placeholder = PLACEHOLDER_LICENSING_TEXT[license]
        license_path = os.path.join(file_path, license)
        license_exists = os.path.exists(license_path)
        entry_found = False
        for i, nameRecord in enumerate(font['name'].names):
            if nameRecord.nameID != NAMEID_LICENSE_DESCRIPTION:
                new_names.append(nameRecord)
            else:
                entry_found = True
                value = nameRecord.string.decode(nameRecord.getEncoding())
                if value != placeholder and license_exists:
                    logging.error('HOTFIXED: License file {} exists but NameID'
                                  ' value is not specified for that.'.format(license))
                    new_name = makeNameRecord(placeholder,
                                              NAMEID_LICENSE_DESCRIPTION,
                                              font['name'].names[i].platformID,
                                              font['name'].names[i].platEncID,
                                              font['name'].names[i].langID)
                    new_names.append(new_name)
                    names_changed = True
                if value == placeholder and license_exists==False:
                    logging.error('Valid licensing specified on NameID 13 but'
                                  ' a corresponding {} file was not found.'.format(license))
        if not entry_found and license_exists:
            new_name = makeNameRecord(placeholder,
                                      NAMEID_LICENSE_DESCRIPTION,
                                      PLATFORM_ID_WINDOWS,
                                      PLAT_ENC_ID_UCS2,
                                      LANG_ID_ENGLISH_USA)
            new_names.append(new_name)
            names_changed = True
            logging.error("HOTFIXED: Font lacks NameID 13. A proper licensing entry was set.")

    if names_changed:
        font['name'].names = new_names
    else:
        logging.info("OK: licensing entry on name table is correctly set.")

    #----------------------------------------------------
    logging.debug("Check license and license URL entries")
    # TODO Check license and license URL are correct, hotfix them if not

    #----------------------------------------------------
    logging.debug("Assure theres no 'description' namerecord")
    # TODO Check namerecord 9 ("description") is not there, drop it if so

# TODO: Port these here as well:
#
#    @tags('required') 
#    @autofix('bakery_cli.fixers.OFLLicenseInfoURLFixer') 
#    def test_name_id_ofl_license_url(self): 
#        """ Is the Open Font License specified in name ID 14 (License info URL)? """ 
#        fixer = OFLLicenseInfoURLFixer(self, self.operator.path) 
#        text = fixer.get_licensecontent() 
#        fontLicensePath = os.path.join(os.path.dirname(self.operator.path), 'OFL.txt') 
# 
#        isLicense = False 
#        for nameRecord in fixer.font['name'].names: 
#            if nameRecord.nameID == NAMEID_LICENSE_INFO_URL: 
#                value = getNameRecordValue(nameRecord) 
#                isLicense = os.path.exists(fontLicensePath) or text in value 
#        self.assertFalse(isLicense and bool(fixer.validate())) 
# 
#    @tags('required') 
#    @autofix('bakery_cli.fixers.ApacheLicenseInfoURLFixer') 
#    def test_name_id_apache_license_url(self): 
#        """ Is the Apache License specified in name ID 14 (License info URL)? """ 
#        fixer = ApacheLicenseInfoURLFixer(self, self.operator.path) 
#        text = fixer.get_licensecontent() 
#        fontLicensePath = os.path.join(os.path.dirname(self.operator.path), 'LICENSE.txt') 
# 
#        isLicense = False 
#        for nameRecord in fixer.font['name'].names: 
#            if nameRecord.nameID == NAMEID_LICENSE_INFO_URL: 
#                value = getNameRecordValue(nameRecord) 
#                isLicense = os.path.exists(fontLicensePath) or text in value 
#        self.assertFalse(isLicense and bool(fixer.validate()))
 
    #----------------------------------------------------
    # TODO: Add a description/rationale to this check here
    logging.debug("Checking name table for items without platformID = 1 (MACHINTOSH)")
    new_names = []
    changed = False
    for name in font['name'].names:
      if (name.platformID != PLATFORM_ID_MACHINTOSH and
          name.nameID not in [NAMEID_COPYRIGHT_NOTICE,
                              NAMEID_FONT_FAMILY_NAME,
                              NAMEID_FONT_SUBFAMILY_NAME,
                              NAMEID_UNIQUE_FONT_IDENTIFIER,
                              NAMEID_FULL_FONT_NAME,
                              NAMEID_VERSION_STRING,
                              NAMEID_POSTSCRIPT_NAME,
                              NAMEID_COMPATIBLE_FULL_MACONLY
                             ]) or \
         (name.platformID == PLATFORM_ID_MACHINTOSH and
          name.nameID in [NAMEID_FONT_FAMILY_NAME,
                          NAMEID_FONT_SUBFAMILY_NAME,
                          NAMEID_FULL_FONT_NAME,
                          NAMEID_POSTSCRIPT_NAME
                         ]): #see https://github.com/googlefonts/fontbakery/issues/649
        new_names.append(name)
      else:
        changed = True
    if changed:
      font['name'].names = new_names
      logging.error("HOTFIXED: some name table items with platformID=1 were removed")
    else:
      logging.info("OK: name table has only the bare-minimum records with platformID=1")

    #----------------------------------------------------
    logging.debug("Removing name table entries with 'opyright' substring")
    new_names = []
    changed = False
    for name in font['name'].names:
      if 'opyright' in name.string.decode(name.getEncoding())\
         and record.nameID == NAMEID_DESCRIPTION:
        changed = True
        continue
      new_names.append(name)
    if changed:
      font['name'].names = new_names
      logging.error("HOTFIXED: some name table items with 'opyright' substring were removed")
    else:
      logging.info("OK: No 'opyright' substring found on name table entries.")

    #----------------------------------------------------
    logging.debug("StyleName recomendadion")
    font_style_name = ""
    for entry in font['name'].names:
        if entry.nameID == NAMEID_FONT_SUBFAMILY_NAME:
            font_style_name = entry.string
            break

    if font_style_name in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
        new_value = font_style_name
        logger.error('OK: {}: Fixed: Windows-only Opentype-specific StyleName set'
                     ' to "{}".'.format(font_file, font_style_name))
    else:
        logger.error('OK: {}: Warning: Windows-only Opentype-specific StyleName set to "Regular"'
                     ' as a default value. Please verify if this is correct.'.format(font_file))
        new_value = 'Regular'

    found = False
    for entry in font['name'].names:
        if entry.nameID != NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME\
           or entry.platformID != PLATFORM_ID_WINDOWS:
            new_names.append(entry)
            continue
        found = True
        entry.string = new_value.encode(entry.getEncoding())
        new_names.append(entry)
    font['name'].names = new_names
    if not found:
        font['name'].setName(new_value, NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME,
                             PLATFORM_ID_WINDOWS,
                             PLAT_ENC_ID_UCS2,
                             LANG_ID_ENGLISH_USA)

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
    # if more than 80% of glyphs have the same width, set monospaced metadata
    monospace_detected = occurrences > 0.80 * len(glyphs)
    if monospace_detected:
        assert_table_entry('post', 'isFixedPitch', IS_FIXED_WIDTH_MONOSPACED)
        assert_table_entry('hhea', 'advanceWidthMax', width_max)
        assert_table_entry('OS/2', 'panose.bProportion', PANOSE_PROPORTION_MONOSPACED)
        # assert_table_entry('OS/2', 'xAvgCharWidth', width_max) #FIXME: Felipe: This needs to be discussed with Dave
        outliers = len(glyphs) - occurrences
        if outliers > 0:
            # If any glyphs are outliers, note them
            unusually_spaced_glyphs = [g for g in glyphs if font['hmtx'].metrics[g][0] != most_common_width]
            outliers_percentage = 100 - (100.0 * occurrences/len(glyphs))
            # FIXME strip glyphs named .notdef .null etc from the unusually_spaced_glyphs list
            log_results("Font is monospaced but {} glyphs".format(outliers) +\
                        " ({0:.2f}%) have a different width.".format(outliers_percentage) +\
                        " You should check the widths of: {}".format(unusually_spaced_glyphs))
        else:
            log_results("Font is monospaced.")
    else:
        # it is not monospaced, so unset monospaced metadata
        assert_table_entry('post', 'isFixedPitch', IS_FIXED_WIDTH_NOT_MONOSPACED)
        assert_table_entry('hhea', 'advanceWidthMax', width_max)
        # assert_table_entry('OS/2', 'xAvgCharWidth', width_max) #FIXME: Felipe: This needs to be discussed with Dave
        if font['OS/2'].panose.bProportion == PANOSE_PROPORTION_MONOSPACED:
            assert_table_entry('OS/2', 'panose.bProportion', PANOSE_PROPORTION_ANY)
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
    #
    # Felipe Sanches:
    # I've been inspecting the fontforge python module source code
    # and it seems that the leakage of stderr messages results from
    # an API design flaw in the module implementation.
    # I am not sure if we can hijack those prints. Maybe we would
    # actually need to modify fontforge code itself to achieve that.
    # I'll have to investigate it further in order to provide a
    # better informed analysis.
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
    logging.debug("Checking vertical metrics")
    # Ascent:
    assert_table_entry('hhea', 'ascent', vmetrics_ymax)
    assert_table_entry('OS/2', 'sTypoAscender', vmetrics_ymax)
    assert_table_entry('OS/2', 'usWinAscent', vmetrics_ymax) # FIXME: This should take only Windows ANSI chars
    # Descent:
    assert_table_entry('hhea', 'descent', vmetrics_ymin)
    assert_table_entry('OS/2', 'sTypoDescender', vmetrics_ymin)
    assert_table_entry('OS/2', 'usWinDescent', -vmetrics_ymin) # FIXME: This should take only Windows ANSI chars
    # LineGap:
    assert_table_entry('hhea', 'lineGap', 0)
    assert_table_entry('OS/2', 'sTypoLineGap', 0)
    # unitsPerEm:
    # Felipe: Dave, should we do it here?
    # assert_table_entry('head', 'unitsPerEm', ymax)
    log_results("Vertical metrics.")

    #----------------------------------------------------
    logging.debug("Checking font version fields")
    #FIXME: do we want all fonts a the same family to have the same major and minor version numbers?
    # If so, then we should calculate the max of each major and minor fields in an external "for font" loop
    ttf_version = parse_version_string(str(font['head'].fontRevision))
    if ttf_version == None:
        fixes.append("Could not parse TTF version string on the 'head' table."+\
                     " Please fix it. Current value is '{}'".format(str(font['head'].fontRevision)))
    else:
        for name in font['name'].names:
            if name.nameID == NAMEID_VERSION_STRING:
                encoding = name.getEncoding()
                s = name.string.decode(encoding)
                #TODO: create an assert_ helper for name table entries of specific name IDs ?
                s = "Version {}.{};{}".format(ttf_version[0], ttf_version[1], ttf_version[2])
                new_string = s.encode(encoding)
                if name.string != new_string:
                    fixes.append("NAMEID_VERSION_STRING from {} to {}".format(name.string, new_string))
                    name.string = new_string
        if 'CFF ' in font.keys():
            major, minor, _ = version
            assert_table_entry("CFF ", 'cff.major', int(major))
            assert_table_entry("CFF ", 'cff.minor', int(minor))
    log_results("Font version fields.")

    #----------------------------------------------------
    logging.debug("Digital Signature")
    if "DSIG" in font:
        logging.info("OK: Digital Signature")
    else:
        try:
            from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
            newDSIG = ttLib.newTable("DSIG")
            newDSIG.ulVersion = 1
            newDSIG.usFlag = 1
            newDSIG.usNumSigs = 1
            sig = SignatureRecord()
            sig.ulLength = 20
            sig.cbSignature = 12
            sig.usReserved2 = 0
            sig.usReserved1 = 0
            sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
            sig.ulFormat = 1
            sig.ulOffset = 20
            newDSIG.signatureRecords = [sig]
            font.tables["DSIG"] = newDSIG
        except ImportError:
            error_message = ("The '{}' font does not have an existing"
                             " digital signature proving its authenticity,"
                             " so Fontbakery needs to add one. To do this"
                             " requires version 2.3 or later of Fonttools"
                             " to be installed. Please upgrade at"
                             " https://pypi.python.org/pypi/FontTools/2.4")
            logging.error(error_message.format(file_path))

    #----------------------------------------------------
    logging.debug("Font contains glyphs for whitespace characters?")
    space = getGlyph(font, 0x0020)
    nbsp = getGlyph(font, 0x00A0)
    tab = getGlyph(font, 0x0009)

    missing = []
    if not space: missing.append("space (0x0020)")
    if not nbsp: missing.append("nbsp (0x00A0)")
    if not tab: missing.append("tab (0x0009)")
    if missing != []:
        logging.error("Font is missing the following glyphs: {}.".format(", ".join(missing)))

    isNbspAdded = False
    isSpaceAdded = False
    try:
        if not nbsp:
            nbsp = addGlyph(font, 0x00A0, 'nbsp')
            isNbspAdded = True
        if not space:
            space = addGlyph(font, 0x0020, 'space')
            isSpaceAdded = True
    except Exception as ex:
        logging.error(ex)

    #----------------------------------------------------
    logging.debug("Font has got propper whitespace glyph names?")
 
    if space != None and space not in ["space", "uni0020"]:
        logging.error('{}: Glyph 0x0020 is called "{}": Change to "space" or "uni0020"'.format(file_path, space))

    if nbsp != None and nbsp not in ["nbsp", "uni00A0", "nonbreakingspace", "nbspace"]:
        logging.error('HOTFIXED: {}: Glyph 0x00A0 is called "{}": Change to "nbsp" or "uni00A0"'.format(file_path, nbsp))

    #----------------------------------------------------
    logging.debug("Whitespace glyphs have ink?")

    for g in [space, nbsp]:
        if glyphHasInk(font, g):
            logging.error('HOTFIXED: {}: Glyph "{}" has ink. Fixed: Overwritten by an empty glyph'.format(file_path, g))
            #overwrite existing glyph with an empty one
            font['glyf'].glyphs[g] = ttLib.getTableModule('glyf').Glyph()

    spaceWidth = getWidth(font, space)
    nbspWidth = getWidth(font, nbsp)

    if spaceWidth != nbspWidth or nbspWidth < 0:
        setWidth(font, nbsp, min(nbspWidth, spaceWidth))
        setWidth(font, space, min(nbspWidth, spaceWidth))

        if isNbspAdded:
            msg = 'OK: {} space {} nbsp None: Added nbsp with advanceWidth {}'
            logging.error(msg.format(file_path, spaceWidth, spaceWidth))

        if isSpaceAdded:
            msg = 'OK: {} space None nbsp {}: Added space with advanceWidth {}'
            logging.error(msg.format(file_path, nbspWidth, nbspWidth))

        if nbspWidth > spaceWidth and spaceWidth >= 0:
            msg = 'OK: {} space {} nbsp {}: Fixed space advanceWidth to {}'
            logging.error(msg.format(file_path, spaceWidth, nbspWidth, nbspWidth))
        else:
            msg = 'OK: {} space {} nbsp {}: Fixed nbsp advanceWidth to {}'
            logging.error(msg.format(file_path, spaceWidth, nbspWidth, spaceWidth))
    else:
        logger.info('OK: {} space {} nbsp {}'.format(file_path, spaceWidth, nbspWidth))


    #------------------------------------------------------
    # TODO Run pyfontaine checks for subset coverage, using the thresholds in add_font.py. See https://github.com/googlefonts/fontbakery/issues/594

    #----------------------------------------------------    
    logging.debug("Check no problematic formats") # See https://github.com/googlefonts/fontbakery/issues/617
    # Font contains all required tables?
    tables = set(font.reader.tables.keys())
    glyphs = set(['glyf'] if 'glyf' in font.keys() else ['CFF '])
    if (REQUIRED_TABLES | glyphs) - tables:
        desc = "Font is missing required tables: [%s]" % ', '.join(str(t) for t in (REQUIRED_TABLES | glyphs - tables))
        if OPTIONAL_TABLES & tables:
            desc += " but includes optional tables %s" % ', '.join(str(t) for t in (OPTIONAL_TABLES & tables))
        fixes.append(desc)
    log_results("Check no problematic formats. ", hotfix=False)

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
    logging.debug("Version format is correct in NAME table?")
    def is_valid_version_format(value):
      return re.match(r'Version\s0*[1-9]+\.\d+', value)

    version_string = get_name_string(font, NAMEID_VERSION_STRING)
    if version_string and is_valid_version_format(version_string):
      logging.info('OK: Version format in NAME table is correct.')
    else:
      logging.error(('The NAMEID_VERSION_STRING (nameID={}) value must follow '
                     'the pattern Version X.Y. Current value: {}').format(NAMEID_VERSION_STRING, version_string))

    #----------------------------------------------------
    logging.debug("Glyph names are all valid?")
    known_good_names = ['.notdef', '.null']
    bad_names = []
    #we should extend this list according to the opentype spec
    for _, glyphName in enumerate(font.getGlyphOrder()):
      if glyphName in known_good_names:
        continue
      if not re.match(r'(?![.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyphName):
        bad_names.append(glyphName)

    if len(bad_names) == 0:
      logging.info('OK: Glyph names are all valid.')
    else:
      logging.error(('The following glyph names do not comply with naming conventions: {}'
                     ' A glyph name may be up to 31 characters in length,'
                     ' must be entirely comprised of characters from'
                     ' the following set:'
                     ' A-Z a-z 0-9 .(period) _(underscore). and must not'
                     ' start with a digit or period. There are a few exceptions'
                     ' such as the special character ".notdef". The glyph names'
                     ' "twocents", "a1", and "_" are all valid, while "2cents"'
                     ' and ".twocents" are not.').format(bad_names))

    #----------------------------------------------------
    logging.debug("Font contains unique glyph names?")
    # (Duplicate glyph names prevent font installation on Mac OS X.)
    glyphs = []
    duplicated_glyphIDs = []
    for _, g in enumerate(font.getGlyphOrder()):
      glyphID = re.sub(r'#\w+', '', g)
      if glyphID in glyphs:
        duplicated_glyphIDs.append(glyphID)
      else:
        glyphs.append(glyphID)

    if len(duplicated_glyphIDs) == 0:
      logging.info("OK: Font contains unique glyph names.")
    else:
      logging.error("The following glyph IDs occur twice: " % duplicated_glyphIDs)

    #----------------------------------------------------
    logging.debug("No glyph is incorrectly named?")
    bad_glyphIDs = []
    for _, g in enumerate(font.getGlyphOrder()):
      if re.search(r'#\w+$', g):
        bad_glyphIDs.append(glyphID)

    if len(bad_glyphIDs) == 0:
      logging.info("OK: Font does not have any incorrectly named glyph.")
    else:
      logging.error("The following glyph IDs are incorrectly named: " % bad_glyphIDs)

    #----------------------------------------------------
    logging.debug("EPAR table present in font?")
    if not 'EPAR' in font:
      logging.error('Font is missing EPAR table.')
    else:
      logging.info("OK: EPAR table present in font.")

    #----------------------------------------------------
    logging.debug("Is GASP table correctly set?")
    try:
      if not isinstance(font['gasp'].gaspRange, dict):
        logging.error('GASP.gaspRange method value have wrong type')
      else:
        if 65535 not in font['gasp'].gaspRange:
          logging.error("GASP does not have 65535 gaspRange")
        else:
          # XXX: Needs review
          value = font['gasp'].gaspRange[65535]
          if value != 15:
            font['gasp'].gaspRange[65535] = 15
            logging.error('HOTFIXED: gaspRange[65535] value ({}) is not 15'.format(value))
          else:
            logging.info('OK: GASP table is correctly set.')
    except KeyError:
      logging.error('Font is missing the GASP table.')

    #----------------------------------------------------
    logging.debug("Does GPOS table have kerning information?")
    try:
      flaglookup = False
      for lookup in font['GPOS'].table.LookupList.Lookup:
        if lookup.LookupType == 2:  # Adjust position of a pair of glyphs
          flaglookup = lookup
          break  # break for..loop to avoid reading all kerning info
      if not flaglookup:
        logging.error("GPOS table lacks kerning information")
      elif flaglookup.SubTableCount == 0:
        logging.error("GPOS LookupType 2 SubTableCount is zero.")
      elif flaglookup.SubTable[0].PairSetCount == 0:
        logging.error("GPOS flaglookup.SubTable[0].PairSetCount is zero!")
      else:
        logging.info("OK: GPOS table has got kerning information.")
    except KeyError:
      logging.error('Font is missing a "GPOS" table')

    #----------------------------------------------------
    logging.debug("Is there a 'KERN' table declared in the font?")
    try:
      font['KERN']
      logging.error("Font should not have a 'KERN' table")
    except KeyError:
      logging.info("OK: Font does not declare a 'KERN' table.")

    #----------------------------------------------------
    logging.debug("Does full font name begin with the font family name?")
    familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
    fullfontname = get_name_string(font, NAMEID_FULL_FONT_NAME)

    if not familyname:
      logging.error('Font lacks a NAMEID_FONT_FAMILY_NAME entry in the name table.')
    elif not fullfamilyname:
      logging.error('Font lacks a NAMEID_FULL_FONT_NAME entry in the name table.')
    #FIX-ME: I think we should still compare entries
    # even if they have different encodings
    elif (familyname.platformID == fullfontname.platformID
        and familyname.platEncID == fullfontname.platEncID
        and familyname.langID == fullfontname.langID):
      if not familyname.startswith(fullfontname):
        logging.error("Font family name '{}' does not begin with full font name '{}'".format(familyname, fullfontname))
      else:
        logging.info('OK: Full font name begins with the font family name.')
    else:
      logging.error('Encoding mismatch between NAMEID_FONT_FAMILY_NAME and NAMEID_FULL_FONT_NAME entries.')

    #----------------------------------------------------
    # TODO: should this test support CFF as well?
    logging.debug("Is there any unused data at the end of the glyf table?")
    if 'CFF ' not in font:
      logging.info("Skipping test. Not a CFF font.")
    else:
      expected = font['loca'].length
      actual = font['glyf'].length
      diff = actual - expected

      # allow up to 3 bytes of padding
      if diff > 3:
        logging.error(("Glyf table has unreachable data at the end of the table." +\
                       " Expected glyf table length %s (from loca table), got length" +\
                       " %s (difference: %s)") % (expected, actual, diff))
      elif diff < 0:
        logging.error(("Loca table references data beyond the end of the glyf table." +\
                       " Expected glyf table length %s (from loca table), got length" +\
                       " %s (difference: %s)") % (expected, actual, diff))
      else:
        logging.info("OK: There is no unused data at the end of the glyf table.")

    #----------------------------------------------------
    import unicodedata
    def font_has_char(font, c):
      cmap = None
      for table in font['cmap'].tables:
        if table.format == 4:
          cmap = table
          break
      if cmap:
        try:
          x = cmap[ord(unicodedata.lookup(c))]
          logging.info("x={}".format(x))
          return True
        except:
          return False
      else:
        return False

    logging.debug("Font has 'EURO SIGN' character?")
    if font_has_char(font, 'EURO SIGN'):
      logging.info("OK: Font has 'EURO SIGN' character.")
    else:
      logging.error("Font lacks the '%s' character." % 'EURO SIGN')


    #----------------------------------------------------
    logging.debug("Font follows the family naming recommendations?")
    # See http://forum.fontlab.com/index.php?topic=313.0
    bad_entries = []

    # <Postscript name> may contain only a-zA-Z0-9
    # and one hyphen
    name = get_name_string(font, NAMEID_POSTSCRIPT_NAME)
    regex = re.compile(r'[a-z0-9-]+', re.IGNORECASE)
    if name and not regex.match(name):
      bad_entries.append({'field': 'PostScript Name',
                          'error': 'May contain only a-zA-Z0-9 characters and an hyphen'})

    if name and name.count('-') > 1:
      bad_entries.append({'field': 'Postscript Name',
                          'error': 'May contain not more than a single hyphen'})

    name = get_name_string(font, NAMEID_FULL_FONT_NAME)
    if name and len(name) >= 64:
      bad_entries.append({'field': 'Full Font Name',
                          'error': 'exceeds max length (64)'})

    name = get_name_string(font, NAMEID_POSTSCRIPT_NAME)
    if name and len(name) >= 30:
      bad_entries.append({'field': 'PostScript Name',
                          'error': 'exceeds max length (30)'})

    name = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
    if name and len(name) >= 32:
      bad_entries.append({'field': 'Family Name',
                          'error': 'exceeds max length (32)'})

    name = get_name_string(font, NAMEID_FONT_SUBFAMILY_NAME)
    if name and len(name) >= 32:
      bad_entries.append({'field': 'Style Name',
                          'error': 'exceeds max length (32)'})

    name = get_name_string(font, NAMEID_TYPOGRAPHIC_FAMILY_NAME)
    if name and len(name) >= 32:
      bad_entries.append({'field': 'OT Family Name',
                          'error': 'exceeds max length (32)'})

    name = get_name_string(font, NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME)
    if name and len(name) >= 32:
      bad_entries.append({'field': 'OT Style Name',
                          'error': 'exceeds max length (32)'})

    weight_value = None
    if 'OS/2' in font:
      field = 'OS/2 usWeightClass'
      weight_value = font['OS/2'].usWeightClass
    if 'CFF' in font:
      field = 'CFF Weight'
      weight_value = font['CFF'].Weight

    if weight_value != None:
      # <Weight> value >= 250 and <= 900 in steps of 50
      if weight_value % 50 != 0:
        bad_entries.append({'field': field,
                            'error': 'Value has to be in steps of 50.'})
      if weight_value < 250:
        bad_entries.append({'field': field,
                            'error': 'Value can\'t be less than 250.'})
      if weight_value > 900:
        bad_entries.append({'field': field,
                            'error': 'Value can\'t be more than 900.'})

    if len(bad_entries) > 0:
      logging.error('Font fails to follow some family naming recommendations: {}'.format(bad_entries))
    else:
      logging.info('OK: Font follows the family naming recommendations.')

    #----------------------------------------------------
    logging.debug("Font contains magic code in PREP table?")
    magiccode = '\xb8\x01\xff\x85\xb0\x04\x8d'
    if 'CFF ' in font:
      logging.info("Not applicable to a CFF font.")
    else:
      try:
        bytecode = font['prep'].program.getBytecode()
      except KeyError:
        bytecode = ''

      if bytecode == magiccode:
        logging.info("OK: Font contains magic code in PREP table.")
      else:
        logging.error("Failed to find correct magic code in PREP table.")

    #----------------------------------------------------

##########################################################
## Metadata related checks:
##########################################################

    fontdir = os.path.dirname(font_file)
    metadata = os.path.join(fontdir, "METADATA.pb")
    if not os.path.exists(metadata):
      logging.error("{} is missing a METADATA.pb file!".format(file_path))
    else:
      family = get_FamilyProto_Message(metadata)

      #-----------------------------------------------------
      logging.debug("METADATA.pb: Ensure designer simple short name.")
      if len(family.designer.split(' ')) >= 4 or\
         ' and ' in family.designer or\
         '.' in family.designer or\
         ',' in family.designer:
        logging.error('`designer` key must be simple short name')
      else:
        logging.info('OK: designer is a simple short name')

      #-----------------------------------------------------
      logging.debug("METADATA.pb: Fontfamily is listed in Google Font Directory ?")
      url = 'http://fonts.googleapis.com/css?family=%s' % family.name.replace(' ', '+')
      fp = requests.get(url)
      if fp.status_code != 200:
        logging.error('No family found in GWF in %s' % url)
      else:
        logging.info('OK: Font is properly listed in Google Font Directory.')

      #-----------------------------------------------------
      logging.debug("METADATA.pb: Designer exists in GWF profiles.csv ?")
      if family.designer == "":
        logging.error('METADATA.pb field "designer" MUST NOT be empty!')
      else:
        fp = urllib.urlopen(PROFILES_RAW_URL)
        designers = []
        for row in csv.reader(fp):
          if not row:
            continue
          designers.append(row[0].decode('utf-8'))
      if family.designer not in designers:
        logging.error("METADATA.pb: Designer '{}' is not listed in profiles.csv (at '{}')".format(family.designer,
                                                                                                  PROFILES_GIT_URL))
      else:
        logging.info("OK: Found designer '{}' at profiles.csv".format(family.designer))

      #-----------------------------------------------------
      logging.debug("METADATA.pb: check if fonts field only have unique 'full_name' values")
      fonts = {}
      for x in family.fonts:
        fonts[x.full_name] = x
      if len(set(fonts.keys())) != len(family.fonts):
        logging.error("Found duplicated 'full_name' values in METADATA.pb fonts field")
      else:
        logging.info("OK: fonts field only have unique 'full_name' values")

      #-----------------------------------------------------
      logging.debug("METADATA.pb: check if fonts field only contains unique style:weight pairs")
      pairs = {}
      for f in family.fonts:
        styleweight = '%s:%s' % (f.style, f.weight)
        pairs[styleweight] = 1
      if len(set(pairs.keys())) != len(family.fonts):
        logging.error("Found duplicated style:weight pair in METADATA.pb fonts field")
      else:
        logging.info("OK: fonts field only have unique style:weight pairs")

      #-----------------------------------------------------
      logging.debug("METADATA.pb license is 'APACHE2', 'UFL' or 'OFL' ?")
      licenses = ['APACHE2', 'OFL', 'UFL']
      if family.license in licenses:
        logging.info("OK: Font license is declared in METADATA.pb as '{}'".format(family.license))
      else:
        logging.error("METADATA.pb license field ('{}') must be one of the following: {}".format(family.license,
                                                                                                 licenses))

      #-----------------------------------------------------
      logging.debug("METADATA.pb subsets should have at least 'latin'")
      if 'latin' not in family.subsets:
        logging.error("METADATA.pb subsets ({}) missing 'latin'".format(family.subsets))
      else:
        logging.info("OK: METADATA.pb subsets contains at least 'latin'")

      #-----------------------------------------------------
      logging.debug("Copyright notice is the same in all fonts ?")
      copyright = ''
      fail = False
      for font_metadata in family.fonts:
        if copyright and font_metadata.copyright != copyright:
          fail = True
        copyright = font_metadata.copyright
      if fail:
        logging.error('METADATA.pb: Copyright field value is inconsistent across family')
      else:
        logging.info('OK: Copyright is consistent across family')

      #-----------------------------------------------------
      logging.debug("Check that METADATA family values are all the same")
      name = ''
      fail = False
      for font_metadata in family.fonts:
        if name and font_metadata.name != name:
          fail = True
        name = font_metadata.name
      if fail:
        logging.error("METADATA.pb: Family name is not the same in all metadata 'fonts' items.")
      else:
        logging.info("OK: METADATA.pb: Family name is the same in all metadata 'fonts' items.")

      #-----------------------------------------------------
      logging.debug("According GWF standards font should have Regular style.")
      found = False
      for f in family.fonts:
        if f.weight == 400 and f.style == 'normal':
          found = True
      if found:
        logging.info("OK: Font has a Regular style.")
      else:
        logging.error("This font lacks a Regular (style: normal and weight: 400) as required by GWF standards.")

      #-----------------------------------------------------
      # This test will only run if the previous has not failed.
      if found:
        logging.debug("Regular should be 400")
        badfonts = []
        for f in family.fonts:
          if f.full_name.endswith('Regular') and f.weight != 400:
            badfonts.append("{} (weight: {})".format(f.filename, f.weight))
        if len(badfonts) > 0:
          logging.error('METADATA.pb: Regular font weight must be 400. Please fix: {}'.format(', '.join(badfonts)))
        else:
          logging.info('OK: Regular has weight=400')
      #-----------------------------------------------------

      for f in family.fonts:
        if filename == f.filename:
          ###### Here go single-TTF metadata tests #######
          #-----------------------------------------------
          logging.debug("Font on disk and in METADATA.pb have the same family name ?")
          familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if familyname == False:
            logging.error("This font lacks a FONT_FAMILY_NAME entry (nameID={}) in the name table.".format(NAMEID_FONT_FAMILY_NAME))
          else:
            if familyname != f.name:
              msg = 'Unmatched family name in font: TTF has "{}" while METADATA.pb has "{}"'
              logging.error(msg.format(familyname, f.name))
            else:
              logging.info("OK: Family name '{}' is identical in METADATA.pb and on the TTF file.".format(f.name))

          #-----------------------------------------------
          logging.debug("Checks METADATA.pb 'postScriptName' matches TTF 'postScriptName'")
          postscript_name = get_name_string(font, NAMEID_POSTSCRIPT_NAME)
          if postscript_name == False:
            logging.error("This font lacks a POSTSCRIPT_NAME entry (nameID={}) in the name table.".format(NAMEID_POSTSCRIPT_NAME))
          else:
            if postscript_name != f.post_script_name:
              msg = 'Unmatched postscript name in font: TTF has "{}" while METADATA.pb has "{}"'
              logging.error(msg.format(postscript_name, f.post_script_name))
            else:
              logging.info("OK: Postscript name '{}' is identical in METADATA.pb and on the TTF file.".format(f.post_script_name))


          #-----------------------------------------------
          logging.debug("METADATA.pb 'fullname' value matches internal 'fullname' ?")
          fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
          if fullname == False:
            logging.error("This font lacks a FULL_FONT_NAME entry (nameID={}) in the name table.".format(NAMEID_FULL_FONT_NAME))
          else:
            if fullname != f.full_name:
              msg = 'Unmatched fullname in font: TTF has "{}" while METADATA.pb has "{}"'
              logging.error(msg.format(fullname, f.full_name))
            else:
              logging.info("OK: Fullname '{}' is identical in METADATA.pb and on the TTF file.".format(fullname))

          #-----------------------------------------------
          logging.debug("METADATA.pb fonts 'name' property should be same as font familyname")
          font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if font_familyname == False:
            logging.error("This font lacks a FONT_FAMILY_NAME entry (nameID={}) in the name table.".format(NAMEID_FONT_FAMILY_NAME))
          else:
            if font_familyname != f.name:
              msg = 'Unmatched familyname in font: TTF has "{}" while METADATA.pb has name="{}"'
              logging.error(msg.format(familyname, f.name))
            else:
              logging.info("OK: Fullname '{}' is identical in METADATA.pb and on the TTF file.".format(fullname))

          #-----------------------------------------------
          logging.debug("METADATA.pb `fullName` matches `postScriptName` ?")
          regex = re.compile(r'\W')
          post_script_name = regex.sub('', f.post_script_name)
          fullname = regex.sub('', f.full_name)
          if fullname != post_script_name:
            msg = 'METADATA.pb full_name="{0}" does not match post_script_name="{1}"'
            logging.error(msg.format(f.full_name, f.post_script_name))
          else:
            logging.info("OK: METADATA.pb fields `fullName` and `postScriptName` have the same value.")

          #-----------------------------------------------
          logging.debug("METADATA.pb `filename` matches `postScriptName` ?")
          regex = re.compile(r'\W')
          if f.post_script_name.endswith('-Regular'):
            logging.error("METADATA.pb postScriptName field ends with '-Regular'")
          else:
            post_script_name = regex.sub('', f.post_script_name)
            filename = regex.sub('', os.path.splitext(f.filename)[0])
            if filename != post_script_name:
              msg = 'METADATA.pb filename="{0}" does not match post_script_name="{1}."'
              if "-Regular" in f.filename:
                msg += " (Consider removing the '-Regular' suffix from the filename.)"
              logging.error(msg.format(f.filename, f.post_script_name))
            else:
              logging.info("OK: METADATA.pb fields `filename` and `postScriptName` have matching values.")

          #-----------------------------------------------
          font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if font_familyname != False:
            logging.debug("METADATA.pb 'name' contains font name in right format ?")
            if font_familyname in f.name:
              logging.info("OK: METADATA.pb 'name' contains font name in right format ?")
            else:
              logging.err("METADATA.pb name='{}' does not match correct font name format.".format(f.name))
            #-----------

            logging.debug("METADATA.pb 'full_name' contains font name in right format ?")
            if font_familyname in f.name:
              logging.info("OK: METADATA.pb 'full_name' contains font name in right format ?")
            else:
              logging.err("METADATA.pb full_name='{}' does not match correct font name format.".format(f.full_name))
            #-----------

            logging.debug("METADATA.pb 'filename' contains font name in right format ?")
            if "".join(str(font_familyname).split()) in f.filename:
              logging.info("OK: METADATA.pb 'filename' contains font name in right format ?")
            else:
              logging.err("METADATA.pb filename='{}' does not match correct font name format.".format(f.filename))
            #-----------

            logging.debug("METADATA.pb 'postScriptName' contains font name in right format ?")
            if "".join(str(font_familyname).split()) in f.post_script_name:
              logging.info("OK: METADATA.pb 'postScriptName' contains font name in right format ?")
            else:
              logging.err("METADATA.pb postScriptName='{}' does not match correct font name format.".format(f.post_script_name))

          #-----------------------------------------------
          logging.debug("Copyright notice matches canonical pattern?")
          almost_matches = re.search(r'(Copyright\s+\(c\)\s+20\d{2}.*)', f.copyright)
          does_match = re.search(r'(Copyright\s+\(c\)\s+20\d{2}.*\(.*@.*.*\))', f.copyright)
          if (does_match != None):
            logging.info("OK: METADATA.pb copyright field matches canonical pattern.")
          else:
            if (almost_matches):
              logging.error("METADATA.pb: Copyright notice is okay, but it lacks an email address. Expected pattern is: 'Copyright 2016 Author Name (name@site.com)'")
            else:
              logging.error("METADATA.pb: Copyright notices should match the folowing pattern: 'Copyright 2016 Author Name (name@site.com)'")

          #-----------------------------------------------
          logging.debug("Copyright notice does not contain Reserved Font Name")
          if 'Reserved Font Name' in f.copyright:
            msg = 'METADATA.pb: copyright field ("%s") contains "Reserved Font Name"'
            logging.error(msg % f.copyright)
          else:
            logging.info('OK: METADATA.pb copyright field does not contain "Reserved Font Name"')

          #-----------------------------------------------
          logging.debug("Copyright notice shouldn't exceed 500 chars")
          if len(f.copyright) > 500:
            logging.error("METADATA.pb: Copyright notice exceeds maximum allowed lengh of 500 characteres.")
          else:
            logging.info("OK: Copyright notice string is shorter than 500 chars.")

          #-----------------------------------------------
          logging.debug("Filename is set canonically?")
          def create_canonical_filename(font_metadata):
            weights = {
              100: 'Thin',
              200: 'ExtraLight',
              300: 'Light',
              400: '',
              500: 'Medium',
              600: 'SemiBold',
              700: 'Bold',
              800: 'ExtraBold',
              900: 'Black'
            }
            style_names = {
             'normal': '',
             'italic': 'Italic'
            }
            familyname = font_metadata.name.replace(' ', '')
            style_weight = '%s%s' % (weights.get(font_metadata.weight),
                                     style_names.get(font_metadata.style))
            if not style_weight:
                style_weight = 'Regular'
            return '%s-%s.ttf' % (familyname, style_weight)

          canonical_filename = create_canonical_filename(f)
          if canonical_filename != f.filename:
            logging.error("METADATA.pb: filename field ('{}') does not match canonical name '{}'".format(f.filename, canonical_filename))
          else:
            logging.info('OK. Filename is set canonically.')

          #-----------------------------------------------
          if f.style == 'italic': #this test only applies to italic fonts
            font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
            font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
            if not font_familyname or not font_fullname:
              pass #these fail scenarios were already tested above
                   #(passing those previous tests is a prerequisite for this one)
            else:
              logging.debug("METADATA.pb font.style `italic` matches font internals?")
              if not bool(font['head'].macStyle & MACSTYLE_ITALIC):
                  logging.error('METADATA.pb style has been set to italic'
                                 ' but font macStyle is improperly set')
              elif not font_familyname.split('-')[-1].endswith('Italic'):
                  logging.error('Font macStyle Italic bit is set but nameID %d ("%s")'
                                 ' is not ended with "Italic"' % (NAMEID_FONT_FAMILY_NAME, font_familyname))
              elif not font_fullname.split('-')[-1].endswith('Italic'):
                  logging.error('Font macStyle Italic bit is set but nameID %d ("%s")'
                                 ' is not ended with "Italic"' % (NAMEID_FULL_FONT_NAME, font_fullname))
              else:
                logging.info('OK: METADATA.pb font.style `italic` matches font internals.')

          #-----------------------------------------------
          if f.style == 'normal': #this test only applies to normal fonts
            font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
            font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
            if not font_familyname or not font_fullname:
              pass #these fail scenarios were already tested above
                   #(passing those previous tests is a prerequisite for this one)
            else:
              logging.debug("METADATA.pb font.style `normal` matches font internals?")
              if bool(font['head'].macStyle & MACSTYLE_ITALIC):
                  logging.error('METADATA.pb style has been set to normal'
                                 ' but font macStyle is improperly set')
              elif font_familyname.split('-')[-1].endswith('Italic'):
                  logging.error('Font macStyle indicates a non-Italic font, but nameID %d ("%s")'
                                 ' ends with "Italic"' % (NAMEID_FONT_FAMILY_NAME, font_familyname))
              elif not font_fullname.split('-')[-1].endswith('Italic'):
                  logging.error('Font macStyle indicates a non-Italic font but nameID %d ("%s")'
                                 ' ends with "Italic"' % (NAMEID_FULL_FONT_NAME, font_fullname))
              else:
                logging.info('OK: METADATA.pb font.style `normal` matches font internals.')

              #----------
              logging.debug("Metadata key-value match to table name fields?")
              if font_familyname != f.name:
                logging.error("METADATA.pb Family name '{}') dos not match name table entry '{}'!".format(f.name, font_familyname))
              elif font_fullname != f.full_name:
                logging.error("METADATA.pb: Fullname ('{}') does not match name table entry '{}'!".format(f.fullname, font_fullname))
              else:
                logging.info("OK: METADATA.pb familyname and fullName fields match corresponding name table entries.")

          #-----------------------------------------------
          logging.debug("Check if fontname is not camel cased.")
          if bool(re.match(r'([A-Z][a-z]+){2,}', f.name)):
            logging.error("METADATA.pb: '%s' is a CamelCased name.".format(f.name) +\
                          " To solve this, simply use spaces instead in the font name.")
          else:
            logging.info("OK: font name is not camel-cased.")

          #-----------------------------------------------
          logging.debug("Check font name is the same as family name.")
          if f.name != family.name:
            logging.error('METADATA.pb: %s: Family name "%s" does not match font name: "%s"'.format(f.filename, family.name, f.name))
          else:
            logging.info('OK: font name is the same as family name.')

          #-----------------------------------------------
          logging.debug("Check that font weight has a canonical value")
          first_digit = f.weight / 100
          if (f.weight % 100) != 0 or (first_digit < 1 or first_digit > 9):
            logging.error("METADATA.pb: The weight is declared as %d which is not a " +\
                          "multiple of 100 between 100 and 900.".format(f.weight))
          else:
            logging.info("OK: font weight has a canonical value.")

          #-----------------------------------------------
          logging.debug("Checking OS/2 usWeightClass matches weight specified at METADATA.pb")
          assert_table_entry('OS/2', 'usWeightClass', f.weight)
          log_results("OS/2 usWeightClass matches weight specified at METADATA.pb")

          #-----------------------------------------------
          weights = {
            'Thin': 100,
            'ThinItalic': 100,
            'ExtraLight': 200,
            'ExtraLightItalic': 200,
            'Light': 300,
            'LightItalic': 300,
            'Regular': 400,
            'Italic': 400,
            'Medium': 500,
            'MediumItalic': 500,
            'SemiBold': 600,
            'SemiBoldItalic': 600,
            'Bold': 700,
            'BoldItalic': 700,
            'ExtraBold': 800,
            'ExtraBoldItalic': 800,
            'Black': 900,
            'BlackItalic': 900,
          }
          #-----------------------------------------------
          logging.debug("Metadata weight matches postScriptName")
          pair = []
          for k, weight in weights.items():
            if weight == f.weight:
              pair.append((k, weight))

          if not pair:
            logging.error('METADATA.pb: Font weight does not match postScriptName')
          elif not (f.post_script_name.endswith('-' + pair[0][0])
                    or f.post_script_name.endswith('-%s' % pair[1][0])):
            logging.error('METADATA.pb: postScriptName ("{}") with weight {} must be '.format(f.post_script_name, pair[0][1]) +\
                          'ended with "{}" or "{}"'.format(pair[0][0], pair[1][0]))
          else:
            logging.info("OK: Weight value matches postScriptName.")

          #-----------------------------------------------
          font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if font_familyname == False:
            pass #skip this test
          else:
            logging.debug("METADATA.pb lists fonts named canonicaly?")
            is_canonical = False
            _weights = []
            for value, intvalue in weights.items():
              if intvalue == font['OS/2'].usWeightClass:
                _weights.append(value)

            for w in _weights:
              canonical_name = "%s %s" % (font_familyname, w)
              if f.full_name == canonical_name:
                is_canonical = True

            if is_canonical:
              logging.info("OK: METADATA.pb lists fonts named canonicaly.")
            else:
              v = map(lambda x: font_familyname + ' ' + x, _weights)
              logging.error('Canonical name in font expected: [%s] but %s' % (v, f.full_name))

          #----------------------------------------------
          def find_italic_in_name_table():
            for entry in font['name'].names:
              if 'italic' in entry.string.decode(entry.getEncoding()).lower():
                return True
            return False

          def is_italic():
            return (font['head'].macStyle & MACSTYLE_ITALIC
                    or font['post'].italicAngle
                    or find_italic_in_name_table())

          if f.style in ['italic', 'normal']:
            logging.debug("Font styles are named canonically?")
            if is_italic() and f.style != 'italic':
              logging.error("%s: The font style is %s but it should be italic" % (f.filename, f.style))
            elif not is_italic() and f.style != 'normal':
              logging.error("%s: The font style is %s but it should be normal" % (f.filename, f.style))
            else:
              logging.info("OK: Font styles are named canonically")

          #----------------------------------------------
          ###### End of single-TTF metadata tests #######

      #-----------------------------------------------------
      # This test only makes sense for monospace fonts:
      if family.category not in ['Monospace', 'MONOSPACE']:
        logging.debug("Skipping monospace-only test. 'Monospace font has hhea.advanceWidthMax equal to each glyph's advanceWidth ?'")
      else:
        logging.debug("Monospace font has hhea.advanceWidthMax equal to each glyph's advanceWidth ?")

        advw = 0
        fail = False
        for glyph_id in font['glyf'].glyphs:
          width = font['hmtx'].metrics[glyph_id][0]
          if advw and width != advw:
            fail = True
          advw = width

        if fail:
          logging.error('Glyph advanceWidth must be same across all glyphs')
        elif advw != font['hhea'].advanceWidthMax:
          msg = ('"hhea" table advanceWidthMax property differs'
                 ' to glyphs advanceWidth [%s, %s]')
          logging.error(msg % (advw, font['hhea'].advanceWidthMax))
          #TODO: compute the percentage of glyphs that do not comply
          #      with the advanceWidth value declared in the hhea table
          #      and report it in the error message.
        else:
          logging.info("OK: hhea.advanceWidthMax is equal to all glyphs' advanceWidth.")

      #----------------------------------------------------

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
