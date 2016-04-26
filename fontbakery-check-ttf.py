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

import os, sys, argparse, glob, logging, subprocess
from bs4 import BeautifulSoup
from fontTools import ttLib
from fontTools.ttLib.tables._n_a_m_e import NameRecord

try:
  from google.protobuf import text_format
except:
  sys.exit("Needs protobuf.\n\nsudo pip install protobuf")

try:
  from bakery_cli.fonts_public_pb2 import FontProto, FamilyProto
except:
  sys.exit("Needs fontbakery.\n\nsudo pip install fontbakery")

#=====================================
# GLOBAL CONSTANTS DEFINITIONS

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
      import requests
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
        assert_table_entry('OS/2', 'xAvgCharWidth', width_max) #FIXME: Felipe: This needs to be discussed with Dave
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
        assert_table_entry('OS/2', 'xAvgCharWidth', width_max) #FIXME: Felipe: This needs to be discussed with Dave
        if font['OS/2'].panose.bProportion != PANOSE_PROPORTION_MODERN: #FIXME: Dave, is this correct now?
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
    # more checks go here

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
    # Metadata related checks:

    fontdir = os.path.dirname(file_path)
    metadata = os.path.join(fontdir, "METADATA.pb")
    if os.path.exists(metadata):
      family = get_FamilyProto_Message(metadata)
      for font in family.fonts:
        logging.debug("METADATA.pb: Ensure designer simple short name.")

        if len(family.designer.split(' ')) >= 4:
          logging.error('`designer` key must be simple short name')
        elif ' and ' in family.designer or\
           '.' in family.designer or\
           ',' in family.designer:
          logging.error('`designer` key must be simple short name')
        else:
          logging.info('OK: designer is a simple short name')

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
