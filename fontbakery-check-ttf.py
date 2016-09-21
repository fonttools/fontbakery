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
from __future__ import print_function
import os
import sys
import tempfile
import argparse
import glob
import logging
import subprocess
import requests
import urllib
import csv
import re
import defusedxml.lxml
import magic
from bs4 import BeautifulSoup
from fontTools import ttLib
from fonts_public_pb2 import FamilyProto
from unidecode import unidecode
from lxml.html import HTMLParser

try:
  from google.protobuf import text_format
except:
  sys.exit("Needs protobuf.\n\nsudo pip install protobuf")

# handy debugging lines:
# import ipdb
# ipdb.set_trace()

# =====================================
# GLOBAL CONSTANTS DEFINITIONS

PROFILES_GIT_URL = ('https://github.com/google/'
                    'fonts/blob/master/designers/profiles.csv')
PROFILES_RAW_URL = ('https://raw.githubusercontent.com/google/'
                    'fonts/master/designers/profiles.csv')

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
               "Black Italic"]

RIBBI_STYLE_NAMES = ["Regular",
                     "Italic",
                     "Bold",
                     "Bold Italic"]

# Weight name to value mapping:
WEIGHTS = {"Thin": 250,
           "ExtraLight": 275,
           "Light": 300,
           "Regular": 400,
           "Medium": 500,
           "SemiBold": 600,
           "Bold": 700,
           "ExtraBold": 800,
           "Black": 900}

# code-points for all "whitespace" chars:
WHITESPACE_CHARACTERS = [
  0x0009, 0x000A, 0x000B, 0x000C, 0x000D, 0x0020,
  0x0085, 0x00A0, 0x1680, 0x2000, 0x2001, 0x2002,
  0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
  0x2009, 0x200A, 0x2028, 0x2029, 0x202F, 0x205F,
  0x3000, 0x180E, 0x200B, 0x200C, 0x200D, 0x2060,
  0xFEFF
]

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

NAMEID_STR = {
  NAMEID_COPYRIGHT_NOTICE: "COPYRIGHT_NOTICE",
  NAMEID_FONT_FAMILY_NAME: "FONT_FAMILY_NAME",
  NAMEID_FONT_SUBFAMILY_NAME: "FONT_SUBFAMILY_NAME",
  NAMEID_UNIQUE_FONT_IDENTIFIER: "UNIQUE_FONT_IDENTIFIER",
  NAMEID_FULL_FONT_NAME: "FULL_FONT_NAME",
  NAMEID_VERSION_STRING: "VERSION_STRING",
  NAMEID_POSTSCRIPT_NAME: "POSTSCRIPT_NAME",
  NAMEID_TRADEMARK: "TRADEMARK",
  NAMEID_MANUFACTURER_NAME: "MANUFACTURER_NAME",
  NAMEID_DESIGNER: "DESIGNER",
  NAMEID_DESCRIPTION: "DESCRIPTION",
  NAMEID_VENDOR_URL: "VENDOR_URL",
  NAMEID_DESIGNER_URL: "DESIGNER_URL",
  NAMEID_LICENSE_DESCRIPTION: "LICENSE_DESCRIPTION",
  NAMEID_LICENSE_INFO_URL: "LICENSE_INFO_URL",
  NAMEID_TYPOGRAPHIC_FAMILY_NAME: "TYPOGRAPHIC_FAMILY_NAME",
  NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME: "TYPOGRAPHIC_SUBFAMILY_NAME",
  NAMEID_COMPATIBLE_FULL_MACONLY: "COMPATIBLE_FULL_MACONLY",
  NAMEID_SAMPLE_TEXT: "SAMPLE_TEXT",
  NAMEID_POSTSCRIPT_CID_NAME: "POSTSCRIPT_CID_NAME",
  NAMEID_WWS_FAMILY_NAME: "WWS_FAMILY_NAME",
  NAMEID_WWS_SUBFAMILY_NAME: "WWS_SUBFAMILY_NAME",
  NAMEID_LIGHT_BACKGROUND_PALETTE: "LIGHT_BACKGROUND_PALETTE",
  NAMEID_DARK_BACKGROUD_PALETTE: "DARK_BACKGROUD_PALETTE"
}

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
IS_FIXED_WIDTH_MONOSPACED = 1  # any non-zero value means monospaced

# Platform IDs:
PLATFORM_ID_UNICODE = 0
PLATFORM_ID_MACINTOSH = 1
PLATFORM_ID_ISO = 2
PLATFORM_ID_WINDOWS = 3
PLATFORM_ID_CUSTOM = 4

PLATID_STR = {
  PLATFORM_ID_UNICODE: "UNICODE",
  PLATFORM_ID_MACINTOSH: "MACINTOSH",
  PLATFORM_ID_ISO: "ISO",
  PLATFORM_ID_WINDOWS: "WINDOWS",
  PLATFORM_ID_CUSTOM: "CUSTOM"
}

# Unicode platform-specific encoding IDs (when platID == 0):
PLAT_ENC_ID_UNICODE_BMP_ONLY = 3

# Windows platform-specific encoding IDs (when platID == 3):
PLAT_ENC_ID_SYMBOL = 0
PLAT_ENC_ID_UCS2 = 1
PLAT_ENC_ID_UCS4 = 10

# Windows-specific langIDs:
LANG_ID_ENGLISH_USA = 0x0409
LANG_ID_MACINTOSH_ENGLISH = 0

PLACEHOLDER_LICENSING_TEXT = {
    'OFL.txt': 'This Font Software is licensed under the SIL Open Font License'
               ', Version 1.1. This license is available with a FAQ at: '
               'http://scripts.sil.org/OFL',
    'LICENSE.txt': 'Licensed under the Apache License, Version 2.0'
}

LICENSE_URL = {
    'OFL.txt': 'http://scripts.sil.org/OFL',
    'LICENSE.txt': 'http://www.apache.org/licenses/LICENSE-2.0'
}

LICENSE_NAME = {
    'OFL.txt': 'Open Font',
    'LICENSE.txt': 'Apache'
}

REQUIRED_TABLES = set(['cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name',
                       'OS/2', 'post'])
OPTIONAL_TABLES = set(['cvt', 'fpgm', 'loca', 'prep',
                       'VORG', 'EBDT', 'EBLC', 'EBSC', 'BASE', 'GPOS',
                       'GSUB', 'JSTF', 'DSIG', 'gasp', 'hdmx', 'kern',
                       'LTSH', 'PCLT', 'VDMX', 'vhea', 'vmtx'])
UNWANTED_TABLES = set(['FFTM', 'TTFA', 'prop'])

# =====================================
# Helper logging class
RED_STR = '\033[1;31;40m{}\033[0m'
GREEN_STR = '\033[1;32;40m{}\033[0m'
YELLOW_STR = '\033[1;33;40m{}\033[0m'
BLUE_STR = '\033[1;34;40m{}\033[0m'
CYAN_STR = '\033[1;36;40m{}\033[0m'
WHITE_STR = '\033[1;37;40m{}\033[0m'

json_report_files = []
ghm_report_files = []


class FontBakeryCheckLogger():
  progressbar = False

  def __init__(self):
    self.reset_report()

  def reset_report(self):
    self.all_checks = []
    self.current_check = None
    self.default_target = None  # All new checks have this target by default
    self.summary = {"Passed": 0,
                    "Hotfixed": 0,
                    "Skipped": 0,
                    "Errors": 0,
                    "Warnings": 0}

  def output_report(self, font_file):
    self.flush()

    total = 0
    for key in self.summary.keys():
      total += self.summary[key]

    print ("\nCheck results summary for '{}':".format(font_file))
    for key in self.summary.keys():
      occurrences = self.summary[key]
      percent = float(100*occurrences)/total
      print ("  {}:"
             "\t{}\t({}%)".format(YELLOW_STR.format(key),
                                  occurrences,
                                  round(percent, 2)))
    print ("  Total: {} checks.\n".format(total))

    if not args.verbose:
      filtered = []
      for check in self.all_checks:
        if check["result"] != "OK":
          filtered.append(check)
      self.all_checks = filtered

    if args.json:
      json_path = font_file + ".fontbakery.json"
      fb.output_json_report(json_path)
    if args.ghm:
      md_path = font_file + ".fontbakery.md"
      fb.output_github_markdown_report(md_path)

  def output_json_report(self, filename):
    import json
    json_data = json.dumps(self.all_checks,
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': '))
    open(filename, 'w').write(json_data)
    json_report_files.append(filename)

  def output_github_markdown_report(self, filename):
    markdown_data = "# Fontbakery check results\n"
    all_checks = {}
    for check in self.all_checks:
      target = check["target"]
      if target in all_checks.keys():
        all_checks[target].append(check)
      else:
        all_checks[target] = [check]

    for target in all_checks.keys():
      markdown_data += "## {}\n".format(target)
      checks = all_checks[target]
      for check in checks:
        msgs = '\n* '.join(check['log_messages'])
        markdown_data += ("### {}\n"
                          "* {}\n\n").format(check['description'], msgs)

    open(filename, 'w').write(markdown_data)
    ghm_report_files.append(filename)

  def update_progressbar(self):
    tick = {
      "OK": GREEN_STR.format('.'),
      "HOTFIX": BLUE_STR.format('H'),
      "ERROR": RED_STR.format('E'),
      "WARNING": YELLOW_STR.format('W'),
      "SKIP": WHITE_STR.format('S'),
      "INFO": CYAN_STR.format('I')
    }
    if self.progressbar is False:
      return
    else:
      print(tick[self.current_check["result"]], end='')
      sys.stdout.flush()

  def flush(self):
    if self.current_check is not None:
      self.update_progressbar()
      self.all_checks.append(self.current_check)
      self.current_check = None

  def new_check(self, desc):
    self.flush()
    logging.debug("Check #{}: {}".format(len(self.all_checks) + 1, desc))
    self.current_check = {"description": desc,
                          "log_messages": [],
                          "result": "unknown",
                          "target": self.default_target}

  def set_target(self, value):
    '''sets target of the current check.
       This can be a folder, or a specific TTF file
       or a METADATA.pb file'''
    if self.current_check:
      self.current_check["target"] = value

  def skip(self, msg):
    self.summary["Skipped"] += 1
    logging.info("SKIP: " + msg)
    self.current_check["log_messages"].append(msg)
    self.current_check["result"] = "SKIP"

  def ok(self, msg):
    self.summary["Passed"] += 1
    logging.info("OK: " + msg)
    self.current_check["log_messages"].append(msg)
    if self.current_check["result"] != "ERROR":
      self.current_check["result"] = "OK"

  def info(self, msg):  # This is just a way for us to keep merely
                        # informative messages on the markdown output
    logging.info("INFO: " + msg)
    self.current_check["log_messages"].append(msg)
    if self.current_check["result"] != "ERROR":
      self.current_check["result"] = "INFO"

  def warning(self, msg):
    self.summary["Warnings"] += 1
    logging.warning(msg)
    self.current_check["log_messages"].append("Warning: " + msg)
    if self.current_check["result"] == "unknown":
      self.current_check["result"] = "WARNING"

  def error(self, msg):
    self.summary["Errors"] += 1
    logging.error(msg)
    self.current_check["log_messages"].append("ERROR: " + msg)
    self.current_check["result"] = "ERROR"

  def hotfix(self, msg):
    self.summary["Hotfixes"] += 1
    logging.info('HOTFIXED: ' + msg)
    self.current_check['log_messages'].append('HOTFIX: ' + msg)
    self.current_check['result'] = "HOTFIX"

fb = FontBakeryCheckLogger()

# =====================================
# HELPER FUNCTIONS
args = None
font = None
fixes = []


def assert_table_entry(tableName, fieldName, expectedValue):
    """ This is a helper function to accumulate
    all fixes that a test performs so that we can
    print them all in a single line by invoking
    the log_results() function.

    Usage example:
    assert_table_entry('post', 'isFixedPitch', 1)
    assert_table_entry('OS/2', 'fsType', 0)
    log_results("Something test.")
    """

    # This is meant to support multi-level field hierarchy
    fields = fieldName.split('.')
    obj = font[tableName]
    for f in range(len(fields)-1):
        obj = getattr(obj, fields[f])
    field = fields[-1]
    value = getattr(obj, field)

    if value != expectedValue:
        setattr(obj, field, expectedValue)
        fixes.append("{} {} from {} to {}".format(tableName,
                                                  fieldName,
                                                  value,
                                                  expectedValue))


def log_results(message, hotfix=True):
  """ Concatenate and log all fixes that happened up to now
  in a good and regular syntax """
  global fixes
  if fixes == []:
    fb.ok(message)
  else:
    if hotfix:
      if args.autofix:
        fb.hotfix("{} Fixes: {}".format(message, " | ".join(fixes)))
      else:
        fb.error(("{} Changes that must be applied to this font:"
                  " {}").format(message, " | ".join(fixes)))
    else:
      fb.error("{} {}".format(message, " | ".join(fixes)))

    # empty the buffer of fixes,
    # in preparation for the next test
    fixes = []


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


def get_name_string(font,
                    nameID,
                    platformID=None,
                    encodingID=None,
                    langID=None):
  results = []
  for entry in font['name'].names:
    if entry.nameID == nameID and \
       (platformID is None or entry.platformID == platformID) and \
       (encodingID is None or entry.platEncID == encodingID) and \
       (langID is None or entry.langID == langID):
      results.append(entry.string.decode(entry.getEncoding()))
  return results


def parse_version_string(s):
    """ Tries to parse a version string as used
        in ttf versioning metadata fields.
        Example of expected format is:
          'Version 01.003; Comments'
    """
    try:
        suffix = ''
        # DC: I think this may be wrong, the ; isnt the only separator,
        # anything not an int is ok
        if ';' in s:
            fields = s.split(';')
            s = fields[0]
            fields.pop(0)
            suffix = ';'.join(fields)
        substrings = s.split('.')
        minor = substrings[-1]
        if ' ' in substrings[-2]:
            major = substrings[-2].split(' ')[-1]
        else:
            major = substrings[-2]
        if suffix:
          return major, minor, suffix
        else:
          return major, minor
    except:
        fb.error("Failed to detect major and minor"
                 " version numbers in '{}'".format(s))


def getGlyph(font, uchar):
    for table in font['cmap'].tables:
        if table.platformID == PLATFORM_ID_WINDOWS and\
           table.platEncID in [PLAT_ENC_ID_UCS2,
                               PLAT_ENC_ID_UCS4]:
          if uchar in table.cmap:
              return table.cmap[uchar]


def getGlyphEncodings(font, names):
    result = set()
    for subtable in font['cmap'].tables:
        if subtable.isUnicode():
            for codepoint, name in subtable.cmap.items():
                if name in names:
                    result.add(codepoint)
    return result


def getWidth(font, glyph):
    return font['hmtx'][glyph][0]


def setWidth(font, glyph, width):
    font['hmtx'][glyph] = (width, font['hmtx'][glyph][1])


def glyphHasInk(font, name):
    """Checks if specified glyph has any ink.
    That is, that it has at least one defined contour associated.
    Composites are considered to have ink if any of their components have ink.
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
    # DC lol, bad people exist, so put a recursion in this recursion
    for glyph_name in glyph.getComponentNames(glyph.components):
        if glyphHasInk(font, glyph_name):
            return True
    return False


def get_FamilyProto_Message(path):
    message = FamilyProto()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, message)
    return message

# set up some command line argument processing
parser = argparse.ArgumentParser(description="Check TTF files"
                                             " for common issues.")
parser.add_argument('arg_filepaths', nargs='+',
                    help='font file path(s) to check.'
                         ' Wildcards like *.ttf are allowed.')
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('-e', '--error', action='store_true',
                    help='Output only errors')
parser.add_argument('-a', '--autofix', action='store_true', default=0)
parser.add_argument('-j', '--json', action='store_true',
                    help='Output check results in JSON format')
parser.add_argument('-m', '--ghm', action='store_true',
                    help='Output check results in GitHub Markdown format')
parser.add_argument('-s', '--skip', action='store_true',
                    help='Skip checks specific to github.com/google/fonts')


# =====================================
# Main sequence of checkers & fixers
def main():
  # set up a basic logging config
  # to include timestamps
  # log_format = '%(asctime)s %(levelname)-8s %(message)s'
  global font, args
  log_format = '%(levelname)-8s %(message)s  '
  logger = logging.getLogger()
  handler = logging.StreamHandler()
  formatter = logging.Formatter(log_format)
  handler.setFormatter(formatter)
  logger.addHandler(handler)

  args = parser.parse_args()
  if args.verbose == 1:
    logger.setLevel(logging.INFO)
  elif args.verbose >= 2:
    logger.setLevel(logging.DEBUG)
  else:
    fb.progressbar = True
    logger.setLevel(logging.CRITICAL)

  if args.error:
    fb.progressbar = False
    logger.setLevel(logging.ERROR)

  # ------------------------------------------------------
  logging.debug("Checking each file is a ttf")
  fonts_to_check = []
  for arg_filepath in sorted(args.arg_filepaths):
    # use glob.glob to accept *.ttf
    for fullpath in glob.glob(arg_filepath):
      file_path, file_name = os.path.split(fullpath)
      if file_name.endswith(".ttf"):
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping '{}' as it does not seem "
                        "to be valid TrueType font file.".format(file_name))
  fonts_to_check.sort()

  if fonts_to_check == []:
    logging.error("None of the fonts are valid TrueType files!")

  # ------------------------------------------------------
  fb.new_check("Checking all files are in the same directory")
  # If the set of font files passed in the command line
  # is not all in the same directory, then we warn the user
  # since the tool will interpret the set of files
  # as belonging to a single family (and it is unlikely
  # that the user would store the files from a single family
  # spreaded in several separate directories).
  failed = False
  target_dir = None
  for target_file in fonts_to_check:
    if target_dir is None:
      target_dir = os.path.split(target_file)[0]
    else:
      if target_dir != os.path.split(target_file)[0]:
        failed = True
        fb.warning("Not all fonts passed in the command line"
                   "are in the same directory. This may lead to"
                   "bad results as the tool will interpret all"
                   "font files as belonging to a single font family.")
        break

  if not failed:
    fb.ok("All files are in the same directory.")

# ---------------------------------------------------------------------
# Perform a few checks on DESCRIPTION files
# ---------------------------------------------------------------------

  fullpath = fonts_to_check[0]  # assuming all fonts are in the same directory
  file_name = os.path.split(fullpath)[0]
  descfile = os.path.join(file_name, "DESCRIPTION.en_us.html")
  if os.path.exists(descfile):
    fb.default_target = descfile
    contents = open(descfile).read()

# ---------------------------------------------------------------------
    fb.new_check("Does DESCRIPTION file contain broken links ?")
    doc = defusedxml.lxml.fromstring(contents, parser=HTMLParser())
    broken_links = []
    for link in doc.xpath('//a/@href'):
      try:
        response = requests.head(link, allow_redirects=True)
        code = response.status_code
        if code != requests.codes.ok:
          broken_links.append(("url: '{}' "
                               "status code: '{}'").format(link,
                                                           code))
      except requests.exceptions.RequestException:
        broken_links.append(link)

    if len(broken_links) > 0:
      fb.error(("The following links are broken"
                " in the DESCRIPTION file:"
                " '{}'").format("', '".join(broken_links)))
    else:
      fb.ok("All links in the DESCRIPTION file look good!")

# ---------------------------------------------------------------------
    fb.new_check("Is this a propper HTML snippet ?")
    try:
      contenttype = magic.from_file(descfile)
      if "HTML" not in contenttype:
        data = open(descfile).read()
        if "<p>" in data and "</p>" in data:
          fb.ok(("{} is a propper"
                 " HTML snippet.").format(descfile))
        else:
          fb.error(("{} is not a propper"
                    " HTML snippet.").format(descfile))
      else:
        fb.ok("{} is a propper HTML file.".format(descfile))
    except AttributeError:
       fb.skip("pythom magic version mismatch: "
               "This check was skipped because the API of the python"
               " magic module version installed in your system does not"
               " provide the from_file method used in"
               " the check implementation.")

# ---------------------------------------------------------------------
    fb.new_check("DESCRIPTION.en_us.html is more than 200 bytes ?")
    statinfo = os.stat(descfile)
    if statinfo.st_size <= 200:
      fb.error("{} must have size larger than 200 bytes".format(descfile))
    else:
      fb.ok("{} is larger than 200 bytes".format(descfile))

# ---------------------------------------------------------------------
    fb.new_check("DESCRIPTION.en_us.html is less than 1000 bytes ?")
    statinfo = os.stat(descfile)
    if statinfo.st_size >= 1000:
      fb.error("{} must have size smaller than 1000 bytes".format(descfile))
    else:
      fb.ok("{} is smaller than 1000 bytes".format(descfile))

# ---------------------------------------------------------------------
# End of DESCRIPTION checks
# ---------------------------------------------------------------------

  # ------------------------------------------------------
  fb.new_check("Checking files are named canonically")
  not_canonical = []

  for font_file in fonts_to_check:
    file_path, filename = os.path.split(font_file)
    if file_path == "":
      fb.set_target("Current Folder")
    else:
      fb.set_target(file_path)  # all font files are in the same dir, right?
    filename_base, filename_extension = os.path.splitext(filename)
    # remove spaces in style names
    style_file_names = [name.replace(' ', '') for name in STYLE_NAMES]
    try:
      family, style = filename_base.split('-')
      if style in style_file_names:
        fb.ok("{} is named canonically".format(font_file))
      else:
        fb.error(('Style name used in "{}" is not canonical.'
                  ' You should rebuild the font using'
                  ' any of the following'
                  ' style names: "{}".').format(font_file,
                                                '", "'.join(STYLE_NAMES)))
        not_canonical.append(font_file)
    except:
        fb.error(("{} is not named canonically.").format(font_file))
        not_canonical.append(font_file)
  if not_canonical:
    print('\nAborted, critical errors with filenames.')
    fb.error(('Please rename these files canonically and try again:\n'
              '{}\n'
              'Canonical names are defined in '
              'https://github.com/googlefonts/gf-docs/blob'
              '/master/ProjectChecklist.md#instance-and-file-naming'
              '').format('\n  '.join(not_canonical)))
    output_folder = os.path.dirname(font_file)
    fb.output_report(output_folder)
    sys.exit(1)

  # ------------------------------------------------------
  logging.debug("Fetching Microsoft's vendorID list")
  url = 'https://www.microsoft.com/typography/links/vendorlist.aspx'
  registered_vendor_ids = {}
  try:
    CACHE_VENDOR_LIST = os.path.join(tempfile.gettempdir(),
                                     'fontbakery-microsoft-vendorlist.cache')
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

# DC This is definitely not step 1, cross-family comes after individual
# in order that individual hotfixes can enable cross-family checks to pass
###########################################################################
## Step 1: Cross-family tests
##         * Validates consistency of data throughout all TTF files
##           in a given family
##         * The list of TTF files in infered from the METADATA.pb file
##         * We avoid testing the same family twice by deduplicating the
##           list of METADATA.pb files first
###########################################################################

  metadata_to_check = []
  for font_file in fonts_to_check:
    fontdir = os.path.dirname(font_file)
    metadata = os.path.join(fontdir, "METADATA.pb")
    if not os.path.exists(metadata):
      logging.error("'{}' is missing a METADATA.pb file!".format(font_file))
    else:
      family = get_FamilyProto_Message(metadata)
      if family not in metadata_to_check:
        metadata_to_check.append([fontdir, family])

  def font_key(f):
    return "{}-{}-{}".format(f.filename,
                             f.post_script_name,
                             f.weight)

  for dirname, family in metadata_to_check:
    ttf = {}
    for f in family.fonts:
      if font_key(f) in ttf.keys():
        # I think this will likely never happen. But just in case...
        logging.error("This is a fontbakery bug."
                      " We need to figure out a better hash-function"
                      " for the font ProtocolBuffer message."
                      " Please file an issue on"
                      " https://github.com/googlefonts/fontbakery/issues/new")
      else:
        ttf[font_key(f)] = ttLib.TTFont(os.path.join(dirname, f.filename))

    if dirname == "":
      fb.default_target = "Current Folder"
    else:
      fb.default_target = dirname
    # -----------------------------------------------------
    fb.new_check("Font designer field is 'unknown' ?")
    if family.designer.lower() == 'unknown':
      fb.error("Font designer field is '{}'.".format(family.designer))
    else:
      fb.ok("Font designer field is not 'unknown'.")

    # -----------------------------------------------------
    fb.new_check("Fonts have consistent underline thickness?")
    fail = False
    uWeight = None
    for f in family.fonts:
      ttfont = ttf[font_key(f)]
      if uWeight is None:
        uWeight = ttfont['post'].underlineThickness
      if uWeight != ttfont['post'].underlineThickness:
        fail = True

    if fail:
      fb.error("Thickness of the underline is not"
               " the same accross this family. In order to fix this,"
               " please make sure that the underlineThickness value"
               " is the same in the POST table of all of this family"
               " font files.")
    else:
      fb.ok("Fonts have consistent underline thickness.")

    # -----------------------------------------------------
    fb.new_check("Fonts have consistent PANOSE proportion?")
    fail = False
    proportion = None
    for f in family.fonts:
      ttfont = ttf[font_key(f)]
      if proportion is None:
        proportion = ttfont['OS/2'].panose.bProportion
      if proportion != ttfont['OS/2'].panose.bProportion:
        fail = True

    if fail:
      fb.error("PANOSE proportion is not"
               " the same accross this family."
               " In order to fix this,"
               " please make sure that the panose.bProportion value"
               " is the same in the OS/2 table of all of this family"
               " font files.")
    else:
      fb.ok("Fonts have consistent PANOSE proportion.")

    # -----------------------------------------------------
    fb.new_check("Fonts have consistent PANOSE family type?")
    fail = False
    familytype = None
    for f in family.fonts:
      ttfont = ttf[font_key(f)]
      if familytype is None:
        familytype = ttfont['OS/2'].panose.bFamilyType
      if familytype != ttfont['OS/2'].panose.bFamilyType:
        fail = True

    if fail:
      fb.error("PANOSE family type is not"
               " the same accross this family."
               " In order to fix this,"
               " please make sure that the panose.bFamilyType value"
               " is the same in the OS/2 table of all of this family"
               " font files.")
    else:
      fb.ok("Fonts have consistent PANOSE family type.")

    # -----------------------------------------------------
    fb.new_check("Fonts have equal numbers of glyphs?")
    counts = {}
    glyphs_count = 0
    fail = False
    for f in family.fonts:
      ttfont = ttf[font_key(f)]
      if not glyphs_count:
        glyphs_count = len(ttfont['glyf'].glyphs)
      if glyphs_count != len(ttfont['glyf'].glyphs):
        fail = True
      counts[f.filename] = glyphs_count

    if fail:
      results_table = ""
      for key in counts.keys():
        results_table += "| {} | {} |\n".format(key,
                                                counts[key])

      fb.error('Fonts have different numbers of glyphs:\n\n'
               '{}\n'.format(results_table))
    else:
      fb.ok("Fonts have equal numbers of glyphs.")

    # -----------------------------------------------------
    fb.new_check("Fonts have equal glyph names?")
    glyphs = None
    fail = False
    for f in family.fonts:
      ttfont = ttf[font_key(f)]
      if not glyphs:
        glyphs = ttfont['glyf'].glyphs
      if glyphs != ttfont['glyf'].glyphs:
        fail = True

    if fail:
      fb.error('Fonts have different glyph names.')
    else:
      fb.ok("Fonts have equal glyph names.")

    # -----------------------------------------------------
    fb.new_check("Fonts have equal unicode encodings?")
    encoding = None
    fail = False
    for f in family.fonts:
      ttfont = ttf[font_key(f)]
      cmap = None
      for table in ttfont['cmap'].tables:
        if table.format == 4:
          cmap = table
          break

      if not encoding:
         encoding = cmap.platEncID

      if encoding != cmap.platEncID:
        fail = True

    if fail:
      fb.error('Fonts have different unicode encodings.')
    else:
      fb.ok("Fonts have equal unicode encodings.")

  # ------------------------------------------------------
  vmetrics_ymin = 0
  vmetrics_ymax = 0
  for font_file in fonts_to_check:
    font = ttLib.TTFont(font_file)
    font_ymin, font_ymax = get_bounding_box(font)
    vmetrics_ymin = min(font_ymin, vmetrics_ymin)
    vmetrics_ymax = max(font_ymax, vmetrics_ymax)

##########################################################################
# Step 2: Single TTF tests
#         * Tests that only check data of each TTF file, but not cross-
#           referencing with other fonts in the family
##########################################################################

 # ------------------------------------------------------
  for font_file in fonts_to_check:
    font = ttLib.TTFont(font_file)
    fb.default_target = font_file
    logging.info("OK: {} opened with fontTools".format(font_file))

    # ----------------------------------------------------
    fb.new_check("Font has post table version 2 ?")
    if font['post'].formatType != 2:
      fb.error(("Post table should be version 2 instead of {}."
                "More info at https://github.com/google/fonts/"
                "issues/215").format(font['post'].formatType))
    else:
      fb.ok("Font has post table version 2.")

    # ----------------------------------------------------
    # OS/2 fsType is a legacy DRM-related field from the 80's
    # It should be disabled in all fonts.
    fb.new_check("Checking OS/2 fsType")
    assert_table_entry('OS/2', 'fsType', 0)
    log_results("fsType is zero.")

    # ----------------------------------------------------
    fb.new_check("Assure valid format for the"
                 " main entries in the name table.")
    # Each entry in the name table has a criteria for validity and
    # this check tests if all entries in the name table are
    # in conformance with that. This check applies only
    # to name IDs 1, 2, 4, 6, 16, 17, 18.
    # It must run before any of the other name table related checks.

    def family_with_spaces(value):
      result = ''
      for c in value:
        if c.isupper():
          result += " "
        result += c
      return result.strip()

    def get_only_weight(value):
      onlyWeight = {"BlackItalic": "Black",
                    "BoldItalic": "",
                    "ExtraBold": "ExtraBold",
                    "ExtraBoldItalic": "ExtraBold",
                    "ExtraLightItalic": "ExtraLight",
                    "LightItalic": "Light",
                    "MediumItalic": "Medium",
                    "SemiBoldItalic": "SemiBold",
                    "ThinItalic": "Thin"}
      if value in onlyWeight.keys():
        return onlyWeight[value]
      else:
        return value

    filename = os.path.split(font_file)[1]
    filename_base = os.path.splitext(filename)[0]
    fname, style = filename_base.split('-')
    fname_with_spaces = family_with_spaces(fname)
    style_with_spaces = style.replace('Italic',
                                      ' Italic').strip()
    only_weight = get_only_weight(style)
    required_nameIDs = [NAMEID_FONT_FAMILY_NAME,
                        NAMEID_FONT_SUBFAMILY_NAME,
                        NAMEID_FULL_FONT_NAME,
                        NAMEID_POSTSCRIPT_NAME]

    if style not in RIBBI_STYLE_NAMES:
      required_nameIDs += [NAMEID_TYPOGRAPHIC_FAMILY_NAME,
                           NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME]
    failed = False
    # The font must have at least these name IDs:
    for nameId in required_nameIDs:
      if len(get_name_string(font, nameId)) == 0:
        failed = True
        fb.error(("Font lacks entry with"
                  " nameId={} ({})").format(nameId,
                                            NAMEID_STR[nameId]))
    for name in font['name'].names:
      string = name.string.decode(name.getEncoding()).strip()
      nameid = name.nameID
      plat = name.platformID
      expected_value = None

      if nameid == NAMEID_FONT_FAMILY_NAME:
        if plat == PLATFORM_ID_MACINTOSH:
          expected_value = fname_with_spaces
        elif plat == PLATFORM_ID_WINDOWS:
          if style in ['Regular',
                       'Italic',
                       'Bold',
                       'Bold Italic']:
            expected_value = fname_with_spaces
          else:
            expected_value = " ".join([fname_with_spaces,
                                       only_weight]).strip()
        else:
          fb.error(("Font should not have a "
                    "[{}({}):{}({})] entry!").format(NAMEID_STR[nameid],
                                                     nameid,
                                                     PLATID_STR[plat],
                                                     plat))
          continue

      elif nameid == NAMEID_FONT_SUBFAMILY_NAME:
        if style_with_spaces not in STYLE_NAMES:
          fb.error(("Style name '{}' inferred from filename"
                    " is not canonical."
                    " Valid options are: {}").format(style_with_spaces,
                                                     STYLE_NAMES))
          continue

        if plat == PLATFORM_ID_MACINTOSH:
          expected_value = style_with_spaces

        elif plat == PLATFORM_ID_WINDOWS:
          if style_with_spaces in ["Bold", "Bold Italic"]:
            expected_value = style_with_spaces
          else:
            if "Italic" in style:
              expected_value = "Italic"
            else:
              expected_value = "Regular"

      elif name.nameID == NAMEID_FULL_FONT_NAME:
        expected_value = "{} {}".format(fname_with_spaces,
                                        style_with_spaces)

      elif name.nameID == NAMEID_POSTSCRIPT_NAME:
        expected_value = "{}-{}".format(fname, style)

      elif nameid == NAMEID_TYPOGRAPHIC_FAMILY_NAME:
        if style not in ['Regular',
                         'Italic',
                         'Bold',
                         'Bold Italic']:
          expected_value = fname_with_spaces

      elif nameid == NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME:
        if style not in ['Regular',
                         'Italic',
                         'Bold',
                         'Bold Italic']:
          expected_value = style_with_spaces

      else:
        # This ignores any other nameID that might
        # be declared in the name table
        continue

      if expected_value is None:
          fb.warning(("Font is not expected to have a "
                      "[{}({}):{}({})] entry!").format(NAMEID_STR[nameid],
                                                       nameid,
                                                       PLATID_STR[plat],
                                                       plat))
      elif string != expected_value:
        failed = True
        fb.error(("[{}({}):{}({})] entry:"
                  " expected '{}'"
                  " but got '{}'").format(NAMEID_STR[nameid],
                                          nameid,
                                          PLATID_STR[plat],
                                          plat,
                                          expected_value,
                                          string))
    if failed is False:
      fb.ok("Main entries in the name table"
            " conform to expected format.")

    # ----------------------------------------------------
    fb.new_check("Checking OS/2 achVendID")
    vid = font['OS/2'].achVendID
    bad_vids = ['UKWN', 'ukwn', 'PfEd']
    if vid is None:
      fb.error("OS/2 VendorID is not set."
               " You should set it to your own 4 character code,"
               " and register that code with Microsoft at"
               " https://www.microsoft.com"
               "/typography/links/vendorlist.aspx")
    elif vid in bad_vids:
      fb.error(("OS/2 VendorID is '{}', a font editor default."
                " You should set it to your own 4 character code,"
                " and register that code with Microsoft at"
                " https://www.microsoft.com"
                "/typography/links/vendorlist.aspx").format(vid))
    elif len(registered_vendor_ids.keys()) > 0:
      if vid in registered_vendor_ids.keys():
        for name in font['name'].names:
          if name.nameID == NAMEID_MANUFACTURER_NAME:
            manufacturer = name.string.decode(name.getEncoding()).strip()
            if manufacturer != registered_vendor_ids[vid].strip():
              fb.warning("VendorID string '{}' does not match"
                         " nameID {} (Manufacturer Name): '{}'".format(
                           unidecode(registered_vendor_ids[vid]).strip(),
                           NAMEID_MANUFACTURER_NAME,
                           unidecode(manufacturer)))

        fb.ok(("OS/2 VendorID is '{}' and registered to '{}'."
               " Is that legit?"
               ).format(vid,
                        unidecode(registered_vendor_ids[vid])))
      elif vid.lower() in [i.lower() for i in registered_vendor_ids.keys()]:
        fb.error(("OS/2 VendorID is '{}' but this is registered"
                  " with different casing."
                  " You should check the case.").format(vid))
      else:
        fb.warning(("OS/2 VendorID is '{}' but"
                    " this is not registered with Microsoft."
                    " You should register it at"
                    " https://www.microsoft.com"
                    "/typography/links/vendorlist.aspx").format(vid))
    else:
      fb.warning(("OS/2 VendorID is '{}'"
                  " but could not be checked against Microsoft's list."
                  " You should check your internet connection"
                  " and try again.").format(vid))

    # ----------------------------------------------------
    fb.new_check("substitute copyright, registered and trademark symbols"
                 " in name table entries")
    failed = False
    replacement_map = [(u"\u00a9", '(c)'),
                       (u"\u00ae", '(r)'),
                       (u"\u2122", '(tm)')]
    for name in font['name'].names:
      new_name = name
      original = unicode(name.string, encoding=name.getEncoding())
      string = unicode(name.string, encoding=name.getEncoding())
      for mark, ascii_repl in replacement_map:
        new_string = string.replace(mark, ascii_repl)
        if string != new_string:
          if args.autofix:
            fb.hotfix(("NAMEID #{} contains symbol that was"
                       " replaced by '{}'").format(name.nameID,
                                                   ascii_repl))
            string = new_string
          else:
            fb.error(("NAMEID #{} contains symbol that should be"
                      " replaced by '{}'").format(name.nameID,
                                                  ascii_repl))
      new_name.string = string.encode(name.getEncoding())
      if string != original:
        failed = True

    if not failed:
      fb.ok("No need to substitute copyright, registered and"
            " trademark symbols in name table entries of this font.")

    # ----------------------------------------------------
    # Determine weight from canonical filename
    file_path, filename = os.path.split(font_file)
    family, style = os.path.splitext(filename)[0].split('-')
    if style == "Italic":
      weight_name = "Regular"
    elif style.endswith("Italic"):
      weight_name = style.replace("Italic", "")
    else:
      weight_name = style

    # ----------------------------------------------------
    fb.new_check("Checking OS/2 usWeightClass")
    value = font['OS/2'].usWeightClass
    expected = WEIGHTS[weight_name]
    if value != expected:
      if args.autofix:
        font['OS/2'].usWeightClass = expected
        fb.hotfix(("OS/2 usWeightClass value was"
                   " fixed from {} to {} ({})."
                   "").format(value, expected, weight_name))
      else:
        fb.error(("OS/2 usWeightClass expected value for"
                  " '{}' is {} but this font has"
                  " {}.").format(weight_name, expected, value))
    else:
      fb.ok("OS/2 usWeightClass value looks good!")

    # ----------------------------------------------------
    def check_bit_entry(font, table, attr, expected, bitmask, bitname):
      value = getattr(font[table], attr)
      name_str = "{} {} {} bit".format(table, attr, bitname)
      if bool(value & bitmask) == expected:
        fb.ok("{} is properly set.".format(name_str))
      else:
        if expected:
          expected_str = "set"
        else:
          expected_str = "reset"
        if args.autofix:
          fb.hotfix("{} has been {}.".format(name_str, expected_str))
          if expected:
            setattr(font[table], attr, value | bitmask)
          else:
            setattr(font[table], attr, value & ~bitmask)
        else:
          fb.error("{} should be {}.".format(name_str, expected_str))

    # ----------------------------------------------------
    fb.new_check("Checking fsSelection REGULAR bit")
    check_bit_entry(font, "OS/2", "fsSelection",
                    "Regular" in style or
                    (style in STYLE_NAMES and
                     style not in RIBBI_STYLE_NAMES and
                     "Italic" not in style),
                    bitmask=FSSEL_REGULAR,
                    bitname="REGULAR")

    # ----------------------------------------------------
    fb.new_check("Checking that italicAngle <= 0")
    value = font['post'].italicAngle
    if value > 0:
      if args.autofix:
        font['post'].italicAngle = -value
        fb.hotfix(("post table italicAngle"
                   " from {} to {}").format(value, -value))
      else:
        fb.error(("post table italicAngle value must be changed"
                  " from {} to {}").format(value, -value))
    else:
      fb.ok("post table italicAngle is {}".format(value))

    # ----------------------------------------------------
    fb.new_check("Checking that italicAngle is less than 20 degrees")
    value = font['post'].italicAngle
    if abs(value) > 20:
      if args.autofix:
        font['post'].italicAngle = -20
        fb.hotfix(("post table italicAngle"
                   " changed from {} to -20").format(value))
      else:
        fb.error(("post table italicAngle value must be"
                  " changed from {} to -20").format(value))
    else:
      fb.ok("OK: post table italicAngle is less than 20 degrees.")

    # ----------------------------------------------------
    fb.new_check("Checking if italicAngle matches font style")
    if "Italic" in style:
      if font['post'].italicAngle == 0:
        fb.error("Font is italic, so post table italicAngle"
                 " should be non-zero.")
      else:
        fb.ok("post table italicAngle matches style name")
    else:
      # Given that the font style is not "Italic",
      # the following call potentially hotfixes
      # the value of italicAngle to zero:
      assert_table_entry('post', 'italicAngle', 0)
      log_results("post table italicAngle matches style name")

    # ----------------------------------------------------
    fb.new_check("Checking fsSelection ITALIC bit")
    check_bit_entry(font, "OS/2", "fsSelection",
                    "Italic" in style,
                    bitmask=FSSEL_ITALIC,
                    bitname="ITALIC")

    # ----------------------------------------------------
    fb.new_check("Checking macStyle ITALIC bit")
    check_bit_entry(font, "head", "macStyle",
                    "Italic" in style,
                    bitmask=MACSTYLE_ITALIC,
                    bitname="ITALIC")

    # ----------------------------------------------------
    fb.new_check("Checking fsSelection BOLD bit")
    check_bit_entry(font, "OS/2", "fsSelection",
                    style in ["Bold", "BoldItalic"],
                    bitmask=FSSEL_BOLD,
                    bitname="BOLD")

    # ----------------------------------------------------
    fb.new_check("Checking macStyle BOLD bit")
    check_bit_entry(font, "head", "macStyle",
                    style in ["Bold", "BoldItalic"],
                    bitmask=MACSTYLE_BOLD,
                    bitname="BOLD")

    # ----------------------------------------------------
    fb.new_check("Check font has a license")
    # Check that OFL.txt or LICENSE.txt exists in the same
    # directory as font_file, if not then warn that there should be one.
    found = False
    for license in ['OFL.txt', 'LICENSE.txt']:
      license_path = os.path.join(file_path, license)
      if os.path.exists(license_path):
        if found is not False:
          fb.error("More than a single license file found."
                   " Please review.")
          found = "multiple"
        else:
          found = license_path

    if found != "multiple":
      if found is False:
        fb.error("No license file was found."
                 " Please add an OFL.txt or a LICENSE.txt file.")
      else:
        fb.ok("Found license at '{}'".format(found))

    # ----------------------------------------------------
    fb.new_check("Check copyright namerecords match license file")
    if found == "multiple":
      fb.skip("This check will only run after the"
              " multiple-licensing file issue is fixed.")
    else:
      failed = False
      for license in ['OFL.txt', 'LICENSE.txt']:
        placeholder = PLACEHOLDER_LICENSING_TEXT[license]
        license_path = os.path.join(file_path, license)
        license_exists = os.path.exists(license_path)
        entry_found = False
        for i, nameRecord in enumerate(font['name'].names):
          if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION:
            entry_found = True
            value = nameRecord.string.decode(nameRecord.getEncoding())
            if value != placeholder and license_exists:
              failed = True
              if args.autofix:
                fb.hotfix(('License file {} exists but'
                           ' NameID {} (LICENSE DESCRIPTION) value'
                           ' on platform {} ({})'
                           ' is not specified for that.'
                           ' Value was: "{}"'
                           ' Expected: "{}"'
                           '').format(license,
                                      NAMEID_LICENSE_DESCRIPTION,
                                      nameRecord.platformID,
                                      PLATID_STR[nameRecord.platformID],
                                      value,
                                      placeholder))
                font['name'].setName(placeholder,
                                     NAMEID_LICENSE_DESCRIPTION,
                                     font['name'].names[i].platformID,
                                     font['name'].names[i].platEncID,
                                     font['name'].names[i].langID)
              else:
                fb.error(('License file {} exists but'
                          ' NameID {} (LICENSE DESCRIPTION) value'
                          ' on platform {} ({})'
                          ' is not specified for that.'
                          ' Value was: "{}"'
                          ' Must be changed to "{}"'
                          '').format(license,
                                     NAMEID_LICENSE_DESCRIPTION,
                                     nameRecord.platformID,
                                     PLATID_STR[nameRecord.platformID],
                                     value,
                                     placeholder))

            if value == placeholder and license_exists is False:
              fb.error(('Valid licensing specified'
                        ' on NameID {} (LICENSE DESCRIPTION)'
                        ' on platform {} ({})'
                        ' but a corresponding "{}" file was'
                        ' not found.'
                        '').format(NAMEID_LICENSE_DESCRIPTION,
                                   nameRecord.platformID,
                                   PLATID_STR[nameRecord.platformID],
                                   license))
        if not entry_found and license_exists:
          failed = True
          if args.autofix:
            font['name'].setName(placeholder,
                                 NAMEID_LICENSE_DESCRIPTION,
                                 PLATFORM_ID_WINDOWS,
                                 PLAT_ENC_ID_UCS2,
                                 LANG_ID_ENGLISH_USA)
            fb.hotfix(("Font lacks NameID {} (LICENSE DESCRIPTION)."
                       " A proper licensing entry was set."
                       "").format(NAMEID_LICENSE_DESCRIPTION))
          else:
            fb.error(("Font lacks NameID {} (LICENSE DESCRIPTION)."
                      " A proper licensing entry must be set."
                      "").format(NAMEID_LICENSE_DESCRIPTION))
      if not failed:
        fb.ok("licensing entry on name table is correctly set.")

    # ----------------------------------------------------
    fb.new_check("Font has a valid license url ?")
    if found == "multiple":
      fb.skip("This check will only run after the"
              " multiple-licensing file issue is fixed.")
      # in case there's no font licensing file
      # we can still run this check for verifying
      # that LICENSE_DESCRIPTION and LICENSE_INFO_URL
      # values are coherent
    else:
      detected_license = False
      for license in ['OFL.txt', 'LICENSE.txt']:
        placeholder = PLACEHOLDER_LICENSING_TEXT[license]
        for nameRecord in font['name'].names:
          string = nameRecord.string.decode(nameRecord.getEncoding())
          if nameRecord.nameID == NAMEID_LICENSE_DESCRIPTION and\
             string == placeholder:
            detected_license = license
            break

      found_good_entry = False
      if detected_license:
        failed = False
        expected = LICENSE_URL[detected_license]
        for nameRecord in font['name'].names:
          if nameRecord.nameID == NAMEID_LICENSE_INFO_URL:
            string = nameRecord.string.decode(nameRecord.getEncoding())
            if string == expected:
              found_good_entry = True
            else:
              if args.autofix:
                pass  # implement-me!
              else:
                failed = True
                fb.error(("Licensing inconsistency in name table entries!"
                          " NameID={} (LICENSE DESCRIPTION) indicates"
                          " {} licensing, but NameID={} (LICENSE URL) has"
                          " '{}'. Expected:"
                          " '{}'").format(NAMEID_LICENSE_DESCRIPTION,
                                          LICENSE_NAME[detected_license],
                                          NAMEID_LICENSE_INFO_URL,
                                          string, expected))
      if not found_good_entry:
        fb.error(("A License URL must be provided in the "
                  "NameID {} (LICENSE INFO URL) entry."
                  "").format(NAMEID_LICENSE_INFO_URL))
      else:
        if failed:
          fb.error(("Even though a valid license URL was seen in NAME table,"
                    " there were also bad entries. Please review"
                    " NameIDs {} (LICENSE DESCRIPTION) and {}"
                    " (LICENSE INFO URL).").format(NAMEID_LICENSE_DESCRIPTION,
                                                   NAMEID_LICENSE_INFO_URL))
        else:
          fb.ok("Font has a valid license URL in NAME table.")

    # ----------------------------------------------------
    fb.new_check(("Description strings in the name table (nameID = {}) must"
                  " not contain copyright info.").format(NAMEID_DESCRIPTION))
    failed = False
    for name in font['name'].names:
      if 'opyright' in name.string.decode(name.getEncoding())\
         and name.nameID == NAMEID_DESCRIPTION:
        failed = True
        del name
    if failed:
      if args.autofix:
        fb.hotfix(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                   " were removed (perhaps added by"
                   " a longstanding FontLab Studio 5.x bug that"
                   " copied copyright notices to them.)"
                   "").format(NAMEID_DESCRIPTION))
      else:
        fb.error(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                  " should be removed (perhaps these were added by"
                  " a longstanding FontLab Studio 5.x bug that"
                  " copied copyright notices to them.)"
                  "").format(NAMEID_DESCRIPTION))
    else:
      fb.ok("Description strings in the name table"
            " do not contain any copyright string.")

    # ----------------------------------------------------
    fb.new_check(("Description strings in the name table (nameID = {}) must"
                  " not exceed 100 characters").format(NAMEID_DESCRIPTION))
    failed = False
    for name in font['name'].names:
      if len(name.string.decode(name.getEncoding())) > 100 \
        and name.nameID == NAMEID_DESCRIPTION:
        if args.autofix:
          del name
        failed = True
    if failed:
      if args.autofix:
        fb.hotfix(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                   " were removed because they"
                   " were longer than 100 characters"
                   ".").format(NAMEID_DESCRIPTION))
      else:
        fb.error(("Namerecords with ID={} (NAMEID_DESCRIPTION)"
                  " are longer than 100 characters"
                  " and should be removed.").format(NAMEID_DESCRIPTION))
    else:
      fb.ok("Description name records do not exceed 100 characters.")

    # ----------------------------------------------------
    fb.new_check("Checking if the font is truly monospaced")
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
        assert_table_entry('OS/2',
                           'panose.bProportion',
                           PANOSE_PROPORTION_MONOSPACED)
        outliers = len(glyphs) - occurrences
        if outliers > 0:
            # If any glyphs are outliers, note them
            unusually_spaced_glyphs =\
              [g for g in glyphs
               if font['hmtx'].metrics[g][0] != most_common_width]
            outliers_percentage = 100 - (100.0 * occurrences/len(glyphs))

            for glyphname in ['.notdef', '.null']:
              if glyphname in unusually_spaced_glyphs:
                unusually_spaced_glyphs.remove(glyphname)

            log_results(("Font is monospaced but {} glyphs"
                         " ({}%) have a different width."
                         " You should check the widths of: {}").format(
                           outliers,
                           outliers_percentage,
                           unusually_spaced_glyphs))
        else:
            log_results("Font is monospaced.")
    else:
        # it is not monospaced, so unset monospaced metadata
        assert_table_entry('post',
                           'isFixedPitch',
                           IS_FIXED_WIDTH_NOT_MONOSPACED)
        assert_table_entry('hhea', 'advanceWidthMax', width_max)
        if font['OS/2'].panose.bProportion == PANOSE_PROPORTION_MONOSPACED:
            assert_table_entry('OS/2',
                               'panose.bProportion',
                               PANOSE_PROPORTION_ANY)
        log_results("Font is not monospaced.")

    # ----------------------------------------------------
    fb.new_check("Check if xAvgCharWidth is correct.")
    if font['OS/2'].version >= 3:
      width_sum = 0
      count = 0
      for glyph_id in font['glyf'].glyphs:
        width = font['hmtx'].metrics[glyph_id][0]
        if width > 0:
          count += 1
          width_sum += width
      if count == 0:
        fb.error("CRITICAL: Found no glyph width data!")
      else:
        expected_value = int(round(width_sum) / count)
        if font['OS/2'].xAvgCharWidth == expected_value:
          fb.ok("xAvgCharWidth is correct.")
        else:
          fb.error(("xAvgCharWidth is {} but should be "
                    "{} which corresponds to the "
                    "average of all glyph widths "
                    "in the font").format(font['OS/2'].xAvgCharWidth,
                                          expected_value))
    else:
      weightFactors = {'a': 64, 'b': 14, 'c': 27, 'd': 35,
                       'e': 100, 'f': 20, 'g': 14, 'h': 42,
                       'i': 63, 'j': 3, 'k': 6, 'l': 35,
                       'm': 20, 'n': 56, 'o': 56, 'p': 17,
                       'q': 4, 'r': 49, 's': 56, 't': 71,
                       'u': 31, 'v': 10, 'w': 18, 'x': 3,
                       'y': 18, 'z': 2, 'space': 166}
      width_sum = 0
      for glyph_id in font['glyf'].glyphs:
        width = font['hmtx'].metrics[glyph_id][0]
        if glyph_id in weightFactors.keys():
          width_sum += (width*weightFactors[glyph_id])
      expected_value = int(width_sum/1000.0 + 0.5)  # round to closest int
      if font['OS/2'].xAvgCharWidth == expected_value:
        fb.ok("xAvgCharWidth value is correct.")
      else:
        fb.error(("xAvgCharWidth is {} but it should be "
                  "{} which corresponds to the weighted "
                  "average of the widths of the latin "
                  "lowercase glyphs in "
                  "the font").format(font['OS/2'].xAvgCharWidth,
                                     expected_value))

    # ----------------------------------------------------
    fb.new_check("Checking with ftxvalidator")
    KNOWN_GOOD_OUTPUT = ''\
                        '<?xml version="1.0" encoding="UTF-8"?>\n'\
                        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"'\
                        ' "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'\
                        '<plist version="1.0">\n'\
                        '<dict>\n'\
                        '    <key>kATSFontTestResultKey</key>\n'\
                        '    <array>\n'\
                        '        <string>'\
                        'kATSFontTestSeverityInformation</string>\n'\
                        '        <string>'\
                        'kATSFontTestSeverityMinorError</string>\n'\
                        '    </array>\n'\
                        '</dict>\n'\
                        '</plist>'

    try:
      ftx_cmd = ["ftxvalidator",
                 "-r",  # Generate a full report
                 "-t", "all",  # execute all tests
                 font_file]
      ftx_output = subprocess.check_output(ftx_cmd,
                                           stderr=subprocess.STDOUT)
      if ftx_output.strip() == KNOWN_GOOD_OUTPUT:
        fb.ok("ftxvalidator passed this file")
      else:
        ftx_cmd = ["ftxvalidator",
                   "-T",  # Human-readable output
                   "-r",  # Generate a full report
                   "-t", "all",  # execute all tests
                   font_file]
        ftx_output = subprocess.check_output(ftx_cmd,
                                             stderr=subprocess.STDOUT)
        fb.error("ftxvalidator output follows:\n\n{}\n".format(ftx_output))

    except subprocess.CalledProcessError, e:
        fb.info(("ftxvalidator returned an error code. Output follows :"
                 "\n\n{}\n").format(e.output))
    except OSError:
      fb.warning("ftxvalidator is not available.")
      pass

    # ----------------------------------------------------
    fb.new_check("Checking with ot-sanitise")
    try:
      ots_output = subprocess.check_output(["ot-sanitise", font_file],
                                           stderr=subprocess.STDOUT)
      if ots_output != "":
        fb.error("ot-sanitise output follows:\n\n{}\n".format(ots_output))
      else:
        fb.ok("ot-sanitise passed this file")
    except subprocess.CalledProcessError, e:
        fb.error(("ot-sanitize returned an error code. Output follows :"
                  "\n\n{}\n").format(e.output))
    except OSError:
      # This is made very prominent with additional line breaks
      fb.warning("\n\n\not-santise is not available!"
                 " You really MUST check the fonts with this tool."
                 " To install it, see"
                 " https://github.com/googlefonts"
                 "/gf-docs/blob/master/ProjectChecklist.md#ots\n\n\n")
      pass

    # ----------------------------------------------------
    try:
      import fontforge
    except ImportError:
      logging.warning("fontforge python module is not available."
                      " To install it, see"
                      " https://github.com/googlefonts/"
                      "gf-docs/blob/master/ProjectChecklist.md#fontforge")
      pass

    try:
      fb.new_check("fontforge validation outputs error messages?")
      if "adobeblank" in font_file:
        fb.skip("Skipping AdobeBlank. This is a Fontbakery bug!")
        break

      # temporary stderr redirection:
      ff_err = os.tmpfile()

      # we do not redirect stderr on Travis because
      # it's making it think the build failed.
      # I'm not exactly why does it happen, but for now we'll
      # workaround the issue by not capturing stderr messages
      # when running on Travis.
      if 'TRAVIS' not in os.environ:
        stderr_backup = os.dup(2)
        os.close(2)
        os.dup2(ff_err.fileno(), 2)

      # invoke font validation
      # via fontforge python module:
      fontforge_font = fontforge.open(font_file)
      validation_state = fontforge_font.validate()

      if 'TRAVIS' not in os.environ:
        # restore default stderr:
        os.dup2(stderr_backup, 2)
        sys.stderr = os.fdopen(2, 'w', 0)

      # handle captured stderr messages:
      ff_err.flush()
      ff_err.seek(0, os.SEEK_SET)
      ff_err_messages = ff_err.read()
      if ff_err_messages != '':
        fb.error(("fontforge did print these messages to stderr:\n"
                  "{}").format(ff_err_messages))
      else:
        fb.ok("fontforge validation did not output any error message.")
      ff_err.close()

      def ff_check(condition, description, err_msg, ok_msg):
        fb.new_check("fontforge-check: {}".format(description))
        if condition is False:
          fb.error("fontforge-check: {}".format(err_msg))
        else:
          fb.ok("fontforge-check: {}".format(ok_msg))

      ff_check("Contours are closed?",
               bool(validation_state & 0x2) is False,
               "Contours are not closed!",
               "Contours are closed.")

      ff_check("Contours do not intersect",
               bool(validation_state & 0x4) is False,
               "There are countour intersections!",
               "Contours do not intersect.")

      ff_check("Contours have correct directions",
               bool(validation_state & 0x8) is False,
               "Contours have incorrect directions!",
               "Contours have correct directions.")

      ff_check("References in the glyph haven't been flipped",
               bool(validation_state & 0x10) is False,
               "References in the glyph have been flipped!",
               "References in the glyph haven't been flipped.")

      ff_check("Glyphs have points at extremas",
               bool(validation_state & 0x20) is False,
               "Glyphs do not have points at extremas!",
               "Glyphs have points at extremas.")

      ff_check("Glyph names referred to from glyphs present in the font",
               bool(validation_state & 0x40) is False,
               "Glyph names referred to from glyphs not present in the font!",
               "Glyph names referred to from glyphs present in the font.")

      ff_check("Points (or control points) are not too far apart",
               bool(validation_state & 0x40000) is False,
               "Points (or control points) are too far apart!",
               "Points (or control points) are not too far apart.")

      ff_check("Not more than 1,500 points in any glyph (a PostScript limit)",
               bool(validation_state & 0x80) is False,
               "There are glyphs with more than 1,500 points!"
               "Exceeds a PostScript limit.",
               "Not more than 1,500 points in any glyph (a PostScript limit).")

      ff_check("PostScript has a limit of 96 hints in glyphs",
               bool(validation_state & 0x100) is False,
               "Exceeds PostScript limit of 96 hints per glyph",
               "Font respects PostScript limit of 96 hints per glyph")

      ff_check("Font doesn't have invalid glyph names",
               bool(validation_state & 0x200) is False,
               "Font has invalid glyph names!",
               "Font doesn't have invalid glyph names.")

      ff_check("Glyphs have allowed numbers of points defined in maxp",
               bool(validation_state & 0x400) is False,
               "Glyphs exceed allowed numbers of points defined in maxp",
               "Glyphs have allowed numbers of points defined in maxp.")

      ff_check("Glyphs have allowed numbers of paths defined in maxp",
               bool(validation_state & 0x800) is False,
               "Glyphs exceed allowed numbers of paths defined in maxp!",
               "Glyphs have allowed numbers of paths defined in maxp.")

      ff_check("Composite glyphs have allowed numbers"
               " of points defined in maxp?",
               bool(validation_state & 0x1000) is False,
               "Composite glyphs exceed allowed numbers"
               " of points defined in maxp!",
               "Composite glyphs have allowed numbers"
               " of points defined in maxp.")

      ff_check("Composite glyphs have allowed numbers"
               " of paths defined in maxp",
               bool(validation_state & 0x2000) is False,
               "Composite glyphs exceed"
               " allowed numbers of paths defined in maxp!",
               "Composite glyphs have"
               " allowed numbers of paths defined in maxp.")

      ff_check("Glyphs instructions have valid lengths",
               bool(validation_state & 0x4000) is False,
               "Glyphs instructions have invalid lengths!",
               "Glyphs instructions have valid lengths.")

      ff_check("Points in glyphs are integer aligned",
               bool(validation_state & 0x80000) is False,
               "Points in glyphs are not integer aligned!",
               "Points in glyphs are integer aligned.")

      # According to the opentype spec, if a glyph contains an anchor point
      # for one anchor class in a subtable, it must contain anchor points
      # for all anchor classes in the subtable. Even it, logically,
      # they do not apply and are unnecessary.
      ff_check("Glyphs have all required anchors.",
               bool(validation_state & 0x100000) is False,
               "Glyphs do not have all required anchors!",
               "Glyphs have all required anchors.")

      ff_check("Glyph names are unique?",
               bool(validation_state & 0x200000) is False,
               "Glyph names are not unique!",
               "Glyph names are unique.")

      ff_check("Unicode code points are unique?",
               bool(validation_state & 0x400000) is False,
               "Unicode code points are not unique!",
               "Unicode code points are unique.")

      ff_check("Do hints overlap?",
               bool(validation_state & 0x800000) is False,
               "Hints should NOT overlap!",
               "Hinds do not overlap.")
    except:
      logging.warning(('fontforge python module could'
                       ' not open {}').format(font_file))

    # ----------------------------------------------------
    fb.new_check("Checking OS/2 usWinAscent & usWinDescent")
    # OS/2 usWinAscent:
    assert_table_entry('OS/2', 'usWinAscent', vmetrics_ymax)
    # OS/2 usWinDescent:
    assert_table_entry('OS/2', 'usWinDescent', abs(vmetrics_ymin))
    log_results("OS/2 usWinAscent & usWinDescent")

    # ----------------------------------------------------
    fb.new_check("Checking Vertical Metric Linegaps")
    if font['hhea'].lineGap != 0:
      fb.warning(("hhea lineGap is not equal to 0"))
    elif font['OS/2'].sTypoLineGap != 0:
      fb.warning(("OS/2 sTypoLineGap is not equal to 0"))
    elif font['OS/2'].sTypoLineGap != font['hhea'].lineGap:
      fb.warning(('OS/2 sTypoLineGap is not equal to hhea lineGap'))
    else:
      fb.ok(('OS/2 sTypoLineGap and hhea lineGap are both 0'))

   # ----------------------------------------------------
    fb.new_check("Checking OS/2 Metrics match hhea Metrics")
    # OS/2 sTypoDescender and sTypoDescender match hhea ascent and descent
    if font['OS/2'].sTypoAscender != font['hhea'].ascent:
      fb.error(("OS/2 sTypoAscender and hhea ascent must be equal"))
    elif font['OS/2'].sTypoDescender != font['hhea'].descent:
      fb.error(("OS/2 sTypoDescender and hhea descent must be equal"))
    else:
      fb.ok("OS/2 sTypoDescender and sTypoDescender match hhea ascent "
            "and descent")

    # ----------------------------------------------------
    fb.new_check("Checking unitsPerEm value is reasonable.")
    upem = font['head'].unitsPerEm
    target_upem = [2**i for i in range(4, 15)]
    target_upem.insert(0, 1000)
    if upem not in target_upem:
      fb.error(("The value of unitsPerEm at the head table"
                " must be either 1000 or a power of "
                "2 between 16 to 16384."
                " Got '{}' instead.").format(upem))
    else:
      fb.ok("unitsPerEm value on the 'head' table is reasonable.")

    # ----------------------------------------------------
    def version_is_newer(a, b):
      a = map(int, a.split("."))
      b = map(int, b.split("."))
      return a > b

    def get_version_from_name_entry(name):
      string = name.string.decode(name.getEncoding())
      # we ignore any comments that
      # may be present in the version name entries
      if ";" in string:
        string = string.split(";")[0]
      # and we also ignore
      # the 'Version ' prefix
      if "Version " in string:
        string = string.split("Version ")[1]
      return string

    def get_expected_version(f):
      expected_version = parse_version_string(str(f['head'].fontRevision))
      for name in f['name'].names:
        if name.nameID == NAMEID_VERSION_STRING:
          name_version = get_version_from_name_entry(name)
          if expected_version is None:
            expected_version = name_version
          else:
            if version_is_newer(name_version, expected_version):
              expected_version = name_version
      return expected_version

    # ----------------------------------------------------
    fb.new_check("Checking font version fields")
    # FIXME: do we want all fonts in the same family to have
    # the same major and minor version numbers?
    # If so, then we should calculate the max of each major and minor fields
    # in an external "for font" loop
    # DC yes we should check this and warn about it but it is not fatal.
    failed = False
    try:
      expected = get_expected_version(font)
    except:
      expected = None
      fb.error("failed to parse font version entries in the name table.")

    if expected is None:
      failed = True
      fb.error("Could not find any font versioning info on the head table"
               " or in the name table entries.")
    else:
      font_revision = str(font['head'].fontRevision)
      expected_str = "{}.{}".format(expected[0],
                                    expected[1])
      if font_revision != expected_str:
        failed = True
        fb.error(("Font revision on the head table ({})"
                  " differs from the expected value ({})"
                  "").format(font_revision, expected))

      expected_str = "Version {}.{}".format(expected[0],
                                            expected[1])
      for name in font['name'].names:
        if name.nameID == NAMEID_VERSION_STRING:
          name_version = name.string.decode(name.getEncoding())
          # change Version 1.007 -> 1.007
          version_stripped = r'(?<=[V|v]ersion )([0-9]{1,4}\.[0-9]{1,5})'
          version_without_comments = re.search(version_stripped,
                                               name_version).group(0)
          comments = re.split(r'(?<=[0-9]{1})[;\s]', name_version)[-1]
          if version_without_comments != expected_str:
            # maybe the version strings differ only
            # on floating-point error, so let's
            # also give it a change by rounding and re-checking...

            try:
              rounded_string = round(float(version_without_comments), 3)
              version = round(float(".".join(expected)), 3)
              if rounded_string != version:
                failed = True
                if comments:
                  fix = "{};{}".format(expected_str, comments)
                else:
                  fix = expected_str
                if args.autofix:
                  fb.hotfix(("NAMEID_VERSION_STRING "
                             "from '{}' to '{}'"
                             "").format(name_version, fix))
                  name.string = fix.encode(name.getEncoding())
                else:
                  fb.error(("NAMEID_VERSION_STRING value '{}'"
                            " does not match expected '{}'"
                            "").format(name_version, fix))
            except:
              failed = True  # give up. it's definitely bad :(
              fb.error("Unable to parse font version info"
                       " from name table entries.")
    if not failed:
      fb.ok("All font version fields look good.")

    # ----------------------------------------------------
    fb.new_check("Digital Signature exists?")
    if "DSIG" in font:
        fb.ok("Digital Signature (DSIG) exists.")
    else:
        try:
            if args.autofix:
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
                fb.hotfix("The font does not have an existing digital"
                          " signature (DSIG), so we just added a dummy"
                          " placeholder that should be enough for the"
                          " applications that require its presence in"
                          " order to work properly.")
            else:
                fb.error("This font lacks a digital signature (DSIG table)"
                         "Some applications may required on (even if only a"
                         " dummy placeholder) in order to work properly.")

        except ImportError:
            error_message = ("The '{}' font does not have an existing"
                             " digital signature (DSIG), so OpenType features"
                             " will not be available in some applications that"
                             " use its presense as a (stupid) heuristic."
                             " So we need to add one. But for that we'll need "
                             "Fonttools v2.3+ so you need to upgrade it. Try:"
                             " $ pip install --upgrade fontTools; or see"
                             " https://pypi.python.org/pypi/FontTools")
            fb.error(error_message.format(font_file))

    # ----------------------------------------------------
    fb.new_check("Font contains the first few mandatory glyphs"
                 " (.null, CR, space)?")
    # It would be good to also check
    # for .notdef (codepoint = unspecified)
    null = getGlyph(font, 0x0000)
    CR = getGlyph(font, 0x000D)
    space = getGlyph(font, 0x0020)

    missing = []
    if null is None: missing.append(".null (0x0000)")
    if CR is None: missing.append("CR (0x00D)")
    if space is None: missing.append("space (0x0020)")
    if missing != []:
        fb.error(("Font is missing"
                  " the following mandatory glyphs:"
                  " {}.").format(", ".join(missing)))
    else:
        fb.ok("Font contains the first few mandatory glyphs"
              " (.null, CR, space).")

    # ----------------------------------------------------
    fb.new_check("Font contains glyphs for whitespace characters?")
    space = getGlyph(font, 0x0020)
    nbsp = getGlyph(font, 0x00A0)
    # tab = getGlyph(font, 0x0009)

    missing = []
    if space is None: missing.append("space (0x0020)")
    if nbsp is None: missing.append("nbsp (0x00A0)")
    # fonts probably don't need an actual tab char
    # if tab is None: missing.append("tab (0x0009)")
    if missing != []:
        fb.error(("Whitespace glyphs missing:"
                  " {}.").format(", ".join(missing)))
    else:
        fb.ok("Font contains glyphs for whitespace characters.")

    # ----------------------------------------------------
    fb.new_check("Font has **proper** whitespace glyph names?")
    if missing != []:
      fb.skip("Because some whitespace glyphs are missing. Fix that before!")
    elif font['post'].formatType == 3.0:
      fb.skip("Font has version 3 post table.")
      # Any further checks for glyph names are pointless
      # because you are really checking names generated by FontTools
      # (or whatever else) that are not actually present in the font.
    else:
      failed = False
      space_enc = getGlyphEncodings(font, ["uni0020", "space"])
      nbsp_enc = getGlyphEncodings(font, ["uni00A0",
                                          "nonbreakingspace",
                                          "nbspace",
                                          "nbsp"])
      if 0x0020 not in space_enc:
        failed = True
        fb.error(('Glyph 0x0020 is called "{}":'
                  ' Change to "space"'
                  ' or "uni0020"').format(space))

      if 0x00A0 not in nbsp_enc:
        if 0x00A0 in space_enc:
          # This is OK.
          # Some fonts use the same glyph for both space and nbsp.
          pass
        else:
          failed = True
          fb.error(('Glyph 0x00A0 is called "{}":'
                    ' Change to "nbsp"'
                    ' or "uni00A0"').format(nbsp))

      if failed is False:
        fb.ok('Font has **proper** whitespace glyph names.')

    # ----------------------------------------------------
    fb.new_check("Whitespace glyphs have ink?")
    if missing != []:
      fb.skip("Because some whitespace glyphs are missing. Fix that before!")
    else:
      failed = False
      for codepoint in WHITESPACE_CHARACTERS:
        g = getGlyph(font, codepoint)
        if g is not None and glyphHasInk(font, g):
          failed = True
          if args.autofix:
            fb.hotfix(('Glyph "{}" has ink.'
                       ' Fixed: Overwritten by'
                       ' an empty glyph').format(g))
            # overwrite existing glyph with an empty one
            font['glyf'].glyphs[g] = ttLib.getTableModule('glyf').Glyph()
          else:
            fb.error(('Glyph "{}" has ink.'
                      ' It needs to be replaced by'
                      ' an empty glyph').format(g))
      if not failed:
        fb.ok("There is no whitespace glyph with ink.")

    # ----------------------------------------------------
    fb.new_check("Whitespace glyphs have coherent widths?")
    if missing != []:
      fb.skip("Because some mandatory whitespace glyphs"
              " are missing. Fix that before!")
    else:
      spaceWidth = getWidth(font, space)
      nbspWidth = getWidth(font, nbsp)

      if spaceWidth != nbspWidth or nbspWidth < 0:
        setWidth(font, nbsp, min(nbspWidth, spaceWidth))
        setWidth(font, space, min(nbspWidth, spaceWidth))

        if nbspWidth > spaceWidth and spaceWidth >= 0:
          if args.autofix:
            msg = 'space {} nbsp {}: Fixed space advanceWidth to {}'
            fb.hotfix(msg.format(spaceWidth, nbspWidth, nbspWidth))
          else:
            msg = ('space {} nbsp {}: Space advanceWidth'
                   ' needs to be fixed to {}')
            fb.error(msg.format(spaceWidth, nbspWidth, nbspWidth))
        else:
          if args.autofix:
            msg = 'space {} nbsp {}: Fixed nbsp advanceWidth to {}'
            fb.hotfix(msg.format(spaceWidth, nbspWidth, spaceWidth))
          else:
            msg = ('space {} nbsp {}: Nbsp advanceWidth'
                   ' needs to be fixed to {}')
            fb.error(msg.format(spaceWidth, nbspWidth, spaceWidth))
      else:
        fb.ok("Whitespace glyphs have coherent widths.")

    # ----------------------------------------------------
    fb.new_check("Checking with pyfontaine")
    try:
      fontaine_output = subprocess.check_output(["pyfontaine",
                                                 "--missing",
                                                 "--set", "gwf_latin",
                                                 font_file],
                                                stderr=subprocess.STDOUT)
      if "Support level: full" not in fontaine_output:
        fb.error("pyfontaine output follows:\n\n{}\n".format(fontaine_output))
      else:
        fb.ok("pyfontaine passed this file")
    except subprocess.CalledProcessError, e:
        fb.error(("pyfontaine returned an error code. Output follows :"
                  "\n\n{}\n").format(e.output))
    except OSError:
      # This is made very prominent with additional line breaks
      fb.warning("\n\n\npyfontaine is not available!"
                 " You really MUST check the fonts with this tool."
                 " To install it, see"
                 " https://github.com/googlefonts"
                 "/gf-docs/blob/master/ProjectChecklist.md#pyfontaine\n\n\n")
      pass

    # ------------------------------------------------------
    fb.new_check("Check no problematic formats")
    # See https://github.com/googlefonts/fontbakery/issues/617
    # Font contains all required tables?
    tables = set(font.reader.tables.keys())
    glyphs = set(['glyf'] if 'glyf' in font.keys() else ['CFF '])
    if (REQUIRED_TABLES | glyphs) - tables:
        missing_tables = [str(t) for t in (REQUIRED_TABLES | glyphs - tables)]
        desc = (("Font is missing required "
                 "tables: [{}]").format(', '.join(missing_tables)))
        if OPTIONAL_TABLES & tables:
            optional_tables = [str(t) for t in (OPTIONAL_TABLES & tables)]
            desc += (" but includes "
                     "optional tables [{}]").format(', '.join(optional_tables))
        fixes.append(desc)
    log_results("Check no problematic formats. ", hotfix=False)

    # ------------------------------------------------------
    fb.new_check("Are there unwanted tables?")
    unwanted_tables_found = []
    for table in font.keys():
      if table in UNWANTED_TABLES:
        unwanted_tables_found.append(table)
        del font[table]

    if len(unwanted_tables_found) > 0:
      if args.autofix:
        fb.hotfix(("Unwanted tables were present"
                   " in the font and were removed:"
                   " {}").format(', '.join(unwanted_tables_found)))
      else:
        fb.error(("Unwanted tables were found"
                  " in the font and should be removed:"
                  " {}").format(', '.join(unwanted_tables_found)))
    else:
      fb.ok("There are no unwanted tables.")

    # ------------------------------------------------------
    fb.new_check("Show hinting filesize impact")
    # current implementation simply logs useful info
    # but there's no fail scenario for this checker.
    ttfautohint_missing = False
    try:
      statinfo = os.stat(font_file)
      hinted_size = statinfo.st_size

      dehinted = tempfile.NamedTemporaryFile(suffix=".ttf",
                                             delete=False)
      subprocess.call(["ttfautohint",
                       "--dehint",
                       font_file,
                       dehinted.name])
      statinfo = os.stat(dehinted.name)
      dehinted_size = statinfo.st_size
      os.unlink(dehinted.name)

      increase = hinted_size - dehinted_size
      change = float(hinted_size)/dehinted_size - 1
      change = int(change*10000)/100.0  # round to 2 decimal pts percentage

      def filesize_formatting(s):
          if s < 1024:
              return "{} bytes".format(s)
          elif s < 1024*1024:
              return "{}kb".format(s/1024)
          else:
              return "{}Mb".format(s/(1024*1024))

      hinted_size = filesize_formatting(hinted_size)
      dehinted_size = filesize_formatting(dehinted_size)
      increase = filesize_formatting(increase)

      results_table = "Hinting filesize impact:\n\n"
      results_table += "|  | {} |\n".format(filename)
      results_table += "|----------|----------|----------|\n"
      results_table += "| Dehinted Size | {} |\n".format(dehinted_size)
      results_table += "| Hinted Size | {} |\n".format(hinted_size)
      results_table += "| Increase | {} |\n".format(increase)
      results_table += "| Change   | {} % |\n".format(change)
      fb.info(results_table)

    except OSError:
      # This is made very prominent with additional line breaks
      ttfautohint_missing = True
      fb.warning("\n\n\nttfautohint is not available!"
                 " You really MUST check the fonts with this tool."
                 " To install it, see"
                 " https://github.com/googlefonts"
                 "/gf-docs/blob/master/ProjectChecklist.md#ttfautohint\n\n\n")
      pass

    # ----------------------------------------------------
    fb.new_check("Version format is correct in NAME table?")

    def is_valid_version_format(value):
      return re.match(r'Version\s0*[1-9]+\.\d+', value)

    failed = False
    version_entries = get_name_string(font, NAMEID_VERSION_STRING)
    if len(version_entries) == 0:
      failed = True
      fb.error(("Font lacks a NAMEID_VERSION_STRING (nameID={})"
                " entry").format(NAMEID_VERSION_STRING))
    for ventry in version_entries:
      if not is_valid_version_format(ventry):
        failed = True
        fb.error(('The NAMEID_VERSION_STRING (nameID={}) value must '
                  'follow the pattern Version X.Y between 1.000 and 9.999.'
                  ' Current value: {}').format(NAMEID_VERSION_STRING,
                                               ventry))
    if not failed:
      fb.ok('Version format in NAME table entries is correct.')

    # ----------------------------------------------------
    # Font has old ttfautohint applied ?
    #
    # 1. find which version was used, grepping the name table or reading
    #    the ttfa table (which are created if the `-I` or `-t` args
    #    respectively were passed to ttfautohint, to record its args in
    #    the ttf file) (there is a pypi package
    #    https://pypi.python.org/pypi/font-ttfa for reading the ttfa table,
    #    although per https://github.com/source-foundry/font-ttfa/issues/1
    #    it might be better to inline the code... :)
    #
    # 2. find which version of ttfautohint is installed
    #    and warn if not available, similar to ots check above
    #
    # 3. rehint the font with the latest version of ttfautohint
    #    using the same options
    fb.new_check("Font has old ttfautohint applied?")

    def ttfautohint_version(values):
      for value in values:
        results = re.search(r'ttfautohint \(v(.*)\)', value)
        if results:
          return results.group(1)

    def installed_ttfa_version(value):
      return re.search(r'ttfautohint ([^-\n]*)(-.*)?\n', value).group(1)

    def installed_version_is_newer(installed, used):
      installed = map(int, installed.split("."))
      used = map(int, used.split("."))
      return installed > used

    if ttfautohint_missing:
      fb.skip("This check requires ttfautohint"
              " to be available in the system.")
    else:
      version_strings = get_name_string(font, NAMEID_VERSION_STRING)
      ttfa_version = ttfautohint_version(version_strings)
      if ttfa_version is None:
        fb.info(("Could not detect which version of"
                 " ttfautohint was used in this font."
                 " It is typically specified as a comment"
                 " in the font version entry of the 'name' table."
                 " Font version string is: '{}'").format(version_strings[0]))
      else:
        ttfa_cmd = ["ttfautohint",
                    "-V"]  # print version info
        ttfa_output = subprocess.check_output(ttfa_cmd,
                                              stderr=subprocess.STDOUT)
        installed_ttfa = installed_ttfa_version(ttfa_output)
        try:
          if installed_version_is_newer(installed_ttfa,
                                        ttfa_version):
            fb.info(("Ttfautohint used in font = {};"
                     " installed = {}; Need to re-run"
                     " with the newer version!").format(ttfa_version,
                                                        installed_ttfa))
          else:
            fb.ok("ttfautohint available in the system is older"
                  " than the one used in the font.")
        except:
          fb.error(("failed to parse ttfautohint version strings:\n"
                    "  * installed = '{}'\n"
                    "  * used = '{}'").format(installed_ttfa,
                                              ttfa_version))

    # ----------------------------------------------------
    fb.new_check("Name table entries should not contain line-breaks")
    failed = False
    for name in font['name'].names:
      string = name.string.decode(name.getEncoding())
      if "\n" in string:
        failed = True
        fb.error(("Name entry {} on platform {} contains"
                  " a line-break.").format(NAMEID_STR[name.nameID],
                                           PLATID_STR[name.platformID]))

    if not failed:
      fb.ok("Name table entries are all single-line (no line-breaks found).")

    # ----------------------------------------------------
    fb.new_check("Glyph names are all valid?")
    bad_names = []
    for _, glyphName in enumerate(font.getGlyphOrder()):
      if glyphName in ['.null', '.notdef']:
        # These 2 names are explicit exceptions
        # in the glyph naming rules
        continue
      if not re.match(r'(?![.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyphName):
        bad_names.append(glyphName)

    if len(bad_names) == 0:
      fb.ok('Glyph names are all valid.')
    else:
      fb.error(('The following glyph names do not comply'
                ' with naming conventions: {}'
                ' A glyph name may be up to 31 characters in length,'
                ' must be entirely comprised of characters from'
                ' the following set:'
                ' A-Z a-z 0-9 .(period) _(underscore). and must not'
                ' start with a digit or period.'
                ' There are a few exceptions'
                ' such as the special character ".notdef".'
                ' The glyph names "twocents", "a1", and "_"'
                ' are all valid, while'
                ' "2cents" and ".twocents" are not.').format(bad_names))

    # ----------------------------------------------------
    fb.new_check("Font contains unique glyph names?")
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
      fb.ok("Font contains unique glyph names.")
    else:
      fb.error(("The following glyph IDs"
                " occur twice: {}").format(duplicated_glyphIDs))

    # ----------------------------------------------------
    fb.new_check("No glyph is incorrectly named?")
    bad_glyphIDs = []
    for _, g in enumerate(font.getGlyphOrder()):
      if re.search(r'#\w+$', g):
        bad_glyphIDs.append(glyphID)

    if len(bad_glyphIDs) == 0:
      fb.ok("Font does not have any incorrectly named glyph.")
    else:
      fb.error(("The following glyph IDs"
                " are incorrectly named: {}").format(bad_glyphIDs))

    # ----------------------------------------------------
    fb.new_check("EPAR table present in font?")
    if 'EPAR' not in font:
      fb.ok('EPAR table not present in font.'
            ' To learn more see'
            ' https://github.com/googlefonts/'
            'fontbakery/issues/818')
    else:
      fb.ok("EPAR table present in font.")

    # ----------------------------------------------------
    fb.new_check("Is GASP table correctly set?")
    try:
      if not isinstance(font["gasp"].gaspRange, dict):
        fb.error("GASP.gaspRange method value have wrong type")
      else:
        failed = False
        if 0xFFFF not in font["gasp"].gaspRange:
          fb.error("GASP does not have 0xFFFF gaspRange")
        else:
          for key in font["gasp"].gaspRange.keys():
            if key != 0xFFFF:
              fb.hotfix(("GASP shuld only have 0xFFFF gaspRange,"
                         " but {} gaspRange was also found"
                         " and has been removed.").format(hex(key)))
              del font["gasp"].gaspRange[key]
              failed = True
            else:
              value = font["gasp"].gaspRange[key]
              if value != 0x0F:
                failed = True
                if args.autofix:
                  font["gasp"].gaspRange[0xFFFF] = 0x0F
                  fb.hotfix("gaspRange[0xFFFF]"
                            " value ({}) is not 0x0F".format(hex(value)))
                else:
                  fb.error(" All flags in GASP range 0xFFFF (i.e. all font"
                           " sizes) must be set to 1.\n"
                           " Rationale:\n"
                           " Traditionally version 0 GASP tables were set"
                           " so that font sizes below 8 ppem had no grid"
                           " fitting but did have antialiasing. From 9-16"
                           " ppem, just grid fitting. And fonts above"
                           " 17ppem had both antialiasing and grid fitting"
                           " toggled on. The use of accelerated graphics"
                           " cards and higher resolution screens make this"
                           " appraoch obsolete. Microsoft's DirectWrite"
                           " pushed this even further with much improved"
                           " rendering built into the OS and apps. In this"
                           " scenario it makes sense to simply toggle all"
                           " 4 flags ON for all font sizes.")
          if not failed:
            fb.ok("GASP table is correctly set.")
    except KeyError:
      fb.error("Font is missing the GASP table.")

    # ----------------------------------------------------
    fb.new_check("Does GPOS table have kerning information?")
    try:
      has_kerning_info = False
      for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType == 2:  # type 2 = Pair Adjustment
          has_kerning_info = True
          break  # avoid reading all kerning info
        elif lookup.LookupType == 9:
          if lookup.SubTable[0].ExtensionLookupType == 2:
            has_kerning_info = True
            break
      if not has_kerning_info:
        fb.error("GPOS table lacks kerning information")
      else:
        fb.ok("GPOS table has got kerning information.")
    except KeyError:
      fb.error('Font is missing a "GPOS" table')

    # ----------------------------------------------------
    fb.new_check("Is there a 'KERN' table declared in the font?")
    try:
      font["KERN"]
      fb.error("Font should not have a 'KERN' table")
    except KeyError:
      fb.ok("Font does not declare a 'KERN' table.")

    # ----------------------------------------------------
    fb.new_check("Does full font name begin with the font family name?")
    familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
    fullfontname = get_name_string(font, NAMEID_FULL_FONT_NAME)

    if len(familyname) == 0:
      fb.error('Font lacks a NAMEID_FONT_FAMILY_NAME entry'
               ' in the name table.')
    elif len(fullfontname) == 0:
      fb.error('Font lacks a NAMEID_FULL_FONT_NAME entry'
               ' in the name table.')
    else:
      # we probably should check all found values are equivalent.
      # and, in that case, then performing the rest of the check
      # with only the first occurences of the name entries
      # will suffice:
      fullfontname = fullfontname[0]
      familyname = familyname[0]

      if not fullfontname.startswith(familyname):
        fb.error(" On the NAME table, the full font name"
                 " (NameID {} - FULL_FONT_NAME: '{}')"
                 " does not begin with font family name"
                 " (NameID {} - FONT_FAMILY_NAME:"
                 " '{}')".format(NAMEID_FULL_FONT_NAME,
                                 familyname,
                                 NAMEID_FONT_FAMILY_NAME,
                                 fullfontname))
      else:
        fb.ok('Full font name begins with the font family name.')

    # ----------------------------------------------------
    fb.new_check("Is there any unused data at the end of the glyf table?")
    if 'CFF ' in font:
      fb.skip("This check does not support CFF fonts.")
    else:
      # -1 because https://www.microsoft.com/typography/otspec/loca.htm
      expected = len(font['loca']) - 1
      actual = len(font['glyf'])
      diff = actual - expected

      # allow up to 3 bytes of padding
      if diff > 3:
        fb.error(("Glyf table has unreachable data at"
                  " the end of the table."
                  " Expected glyf table length {}"
                  " (from loca table), got length"
                  " {} (difference: {})").format(expected, actual, diff))
      elif diff < 0:
        fb.error(("Loca table references data beyond"
                  " the end of the glyf table."
                  " Expected glyf table length {}"
                  " (from loca table), got length"
                  " {} (difference: {})").format(expected, actual, diff))
      else:
        fb.ok("There is no unused data at"
              " the end of the glyf table.")

    # ----------------------------------------------------
    def font_has_char(font, c):
        if c in font['cmap'].buildReversed():
          return len(font['cmap'].buildReversed()[c]) > 0
        else:
          return False

    fb.new_check("Font has 'EURO SIGN' character?")
    if font_has_char(font, 'Euro'):
      fb.ok("Font has 'EURO SIGN' character.")
    else:
      fb.error("Font lacks the '%s' character." % 'EURO SIGN')

    # ----------------------------------------------------
    fb.new_check("Font follows the family naming recommendations?")
    # See http://forum.fontlab.com/index.php?topic=313.0
    bad_entries = []

    # <Postscript name> may contain only a-zA-Z0-9
    # and one hyphen
    regex = re.compile(r'[a-z0-9-]+', re.IGNORECASE)
    for name in get_name_string(font, NAMEID_POSTSCRIPT_NAME):
      if not regex.match(name):
        bad_entries.append({'field': 'PostScript Name',
                            'rec': 'May contain only a-zA-Z0-9'
                                   ' characters and an hyphen'})
      if name.count('-') > 1:
        bad_entries.append({'field': 'Postscript Name',
                            'rec': 'May contain not more'
                                   ' than a single hyphen'})

    for name in get_name_string(font, NAMEID_FULL_FONT_NAME):
      if len(name) >= 64:
        bad_entries.append({'field': 'Full Font Name',
                            'rec': 'exceeds max length (64)'})

    for name in get_name_string(font, NAMEID_POSTSCRIPT_NAME):
      if len(name) >= 30:
        bad_entries.append({'field': 'PostScript Name',
                            'rec': 'exceeds max length (30)'})

    for name in get_name_string(font, NAMEID_FONT_FAMILY_NAME):
      if len(name) >= 32:
        bad_entries.append({'field': 'Family Name',
                            'rec': 'exceeds max length (32)'})

    for name in get_name_string(font, NAMEID_FONT_SUBFAMILY_NAME):
      if len(name) >= 32:
        bad_entries.append({'field': 'Style Name',
                            'rec': 'exceeds max length (32)'})

    for name in get_name_string(font, NAMEID_TYPOGRAPHIC_FAMILY_NAME):
      if len(name) >= 32:
        bad_entries.append({'field': 'OT Family Name',
                            'rec': 'exceeds max length (32)'})

    for name in get_name_string(font, NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME):
      if len(name) >= 32:
        bad_entries.append({'field': 'OT Style Name',
                            'rec': 'exceeds max length (32)'})

    weight_value = None
    if 'OS/2' in font:
      field = 'OS/2 usWeightClass'
      weight_value = font['OS/2'].usWeightClass
    if 'CFF' in font:
      field = 'CFF Weight'
      weight_value = font['CFF'].Weight

    if weight_value is not None:
      # <Weight> value >= 250 and <= 900 in steps of 50
      if weight_value % 50 != 0:
        bad_entries.append({"field": field,
                            "rec": "Value should idealy be a multiple of 50."})
      if weight_value < 250:
        bad_entries.append({"field": field,
                            "rec": "Value should idealy be 250 or more."})
      if weight_value > 900:
        bad_entries.append({"field": field,
                            "rec": "Value should idealy be 900 or less."})

    if len(bad_entries) > 0:
      table = "| Field | Recommendation |\n"
      table += "|----------|----------|\n"

      for bad in bad_entries:
        table += "| {} | {} |\n".format(bad["field"], bad["rec"])
      fb.info(("Font does not follow "
               "some family naming recommendations:\n\n"
               "{}").format(table))
    else:
      fb.ok("Font follows the family naming recommendations.")

    # ----------------------------------------------------
    fb.new_check("Font contains magic code in 'prep' table?")
    magiccode = "\xb8\x01\xff\x85\xb0\x04\x8d"
    # B8 01 FF    PUSHW 0x01FF
    # 85          SCANCTRL (unconditinally turn on
    #                       dropout control mode)
    # B0 04       PUSHB 0x04
    # 8D          SCANTYPE (enable smart dropout control)
    #
    # Smart dropout control means activating rules 1, 2 and 5:
    # Rule 1: If a pixel's center falls within the glyph outline,
    #         that pixel is turned on.
    # Rule 2: If a contour falls exactly on a pixel's center,
    #         that pixel is turned on.
    # Rule 5: If a scan line between two adjacent pixel centers
    #         (either vertical or horizontal) is intersected
    #         by both an on-Transition contour and an off-Transition
    #         contour and neither of the pixels was already turned on
    #         by rules 1 and 2, turn on the pixel which is closer to
    #         the midpoint between the on-Transition contour and
    #         off-Transition contour. This is "Smart" dropout control.
    if "CFF " in font:
      fb.skip("Not applicable to a CFF font.")
    else:
      try:
        bytecode = font['prep'].program.getBytecode()
      except KeyError:
        bytecode = ''

      if magiccode in bytecode:
        fb.ok("Font contains magic code in 'prep' table.")
      else:
        fb.error("Failed to find correct magic code in 'prep' table.")

    # ----------------------------------------------------
    fb.new_check("MaxAdvanceWidth is consistent with values"
                 " in the Hmtx and Hhea tables?")
    hhea_advance_width_max = font['hhea'].advanceWidthMax
    hmtx_advance_width_max = None
    for g in font['hmtx'].metrics.values():
      if hmtx_advance_width_max is None:
        hmtx_advance_width_max = max(0, g[0])
      else:
        hmtx_advance_width_max = max(g[0], hmtx_advance_width_max)

    if hmtx_advance_width_max is None:
      fb.error("Failed to find advance width data in HMTX table!")
    elif hmtx_advance_width_max != hhea_advance_width_max:
      fb.error("AdvanceWidthMax mismatch: expected %s (from hmtx);"
               " got %s (from hhea)") % (hmtx_advance_width_max,
                                         hhea_advance_width_max)
    else:
      fb.ok("MaxAdvanceWidth is consistent"
            " with values in the Hmtx and Hhea tables.")

    # ----------------------------------------------------
    fb.new_check("Font names are consistent across platforms?")
    failed = False
    for name1 in font['name'].names:
      if ((name1.platformID == PLATFORM_ID_WINDOWS) and
         (name1.langID == LANG_ID_ENGLISH_USA)):
        for name2 in font['name'].names:
          if ((name2.platformID == PLATFORM_ID_MACINTOSH) and
             (name2.langID == LANG_ID_MACINTOSH_ENGLISH)):
            if name1.nameID == name2.nameID:
              n1 = get_name_string(font,
                                   name1.nameID,
                                   name1.platformID,
                                   name1.platEncID,
                                   name1.langID)
              n2 = get_name_string(font,
                                   name2.nameID,
                                   name2.platformID,
                                   name2.platEncID,
                                   name2.langID)
            if len(n1) == 0 or len(n2) == 0 or n1[0] != n2[0]:
              failed = True
    if failed:
      fb.error('Entries in "name" table are not'
               ' the same across specific platforms.')
    else:
      fb.ok('Font names are consistent across platforms.')

    # ----------------------------------------------------
    fb.new_check("Are there non-ASCII characters"
                 " in ASCII-only NAME table entries ?")
    bad_entries = []
    for name in font['name'].names:
      # Items with NameID > 18 are expressly for localising
      # the ASCII-only IDs into Hindi / Arabic / etc.
      if name.nameID >= 0 and name.nameID <= 18:
        string = name.string.decode(name.getEncoding())
        try:
          string.encode('ascii')
        except:
          bad_entries.append(name)
    if len(bad_entries) > 0:
      fb.error(('There are {} strings containing'
                ' non-ASCII characters in the ASCII-only'
                ' NAME table entries.').format(len(bad_entries)))
    else:
      fb.ok('None of the ASCII-only NAME table entries'
            ' contain non-ASCII characteres.')

    # ----------------------------------------------------
    # This check is temporarily disabled
    # based on the request at:
    # https://github.com/googlefonts/fontbakery/commit/
    #  23ab884f839d715a664a02d9f9b6c5c6a38bbc45#commitcomment-17761459
    #
    # fb.new_check("Are there unencoded glyphs ?")
    # # fixer at: bakery_cli.fixers.AddSPUAByGlyphIDToCmap
    # cmap = font['cmap']
    # new_cmap = cmap.getcmap(3, 10)
    # if not new_cmap:
    #   for ucs2cmapid in ((PLATFORM_ID_WINDOWS, PLAT_ENC_ID_UCS2),
    #                      (PLATFORM_ID_UNICODE, PLAT_ENC_ID_UNICODE_BMP_ONLY),
    #                      (PLATFORM_ID_WINDOWS, PLAT_ENC_ID_SYMBOL)):
    #     new_cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
    #     if new_cmap:
    #       break
    # unencoded_list = []
    # if new_cmap:
    #   diff = list(set(font.glyphOrder) -
    #               set(new_cmap.cmap.values()) - {'.notdef'})
    #   unencoded_list = [g for g in diff[:] if g != '.notdef']
    #
    # if len(unencoded_list) > 0:
    #   fb.error(("There are unencoded glyphs: "
    #             "[{}]").format(', '.join(unencoded_list)))
    # else:
    #   fb.ok("There are no unencoded glyphs.")

    # ----------------------------------------------------
    fb.new_check("Is font em size (ideally) equal to 1000?")
    if args.skip:
      fb.skip("Skipping this Google-Fonts specific check.")
    else:
      upm_height = font['head'].unitsPerEm
      if upm_height != 1000:
        fb.warning(("font em size ({}) is not"
                    " equal to 1000.").format(upm_height))
      else:
        fb.ok("Font em size is equal to 1000.")

##########################################################
##  Checks ported from:                                 ##
##  https://github.com/mekkablue/Glyphs-Scripts/        ##
##  blob/447270c7a82fa272acc312e120abb20f82716d08/      ##
##  Test/Preflight%20Font.py                            ##
##########################################################

    # ----------------------------------------------------
    fb.new_check("Check for points out of bounds")
    failed = False
    for glyphName in font['glyf'].keys():
      glyph = font['glyf'][glyphName]
      coords, endpts, flags = glyph.getCoordinates(font['glyf'])
      for x, y in coords:
        if x < glyph.xMin or x > glyph.xMax or \
           y < glyph.yMin or y > glyph.yMax or \
           abs(x) > 32766 or abs(y) > 32766:
          failed = True
          fb.error(("Glyph '{}' coordinates ({},{})"
                    " out of bounds!").format(glyphName, x, y))
    if not failed:
      fb.ok("All glyph paths have coordinates within bounds!")

    # ----------------------------------------------------
    fb.new_check("Check glyphs have unique unicode codepoints")
    failed = False
    for subtable in font['cmap'].tables:
      if subtable.isUnicode():
        codepoints = {}
        for codepoint, name in subtable.cmap.items():
          codepoints.setdefault(codepoint, set()).add(name)
        for value in codepoints.keys():
          if len(codepoints[value]) >= 2:
            failed = True
            fb.error(("These glyphs carry the same"
                      " unicode value {}:"
                      " {}").format(value,
                                    ", ".join(codepoints[value])))
    if not failed:
      fb.ok("All glyphs have unique unicode codepoint assignments.")

    # ----------------------------------------------------
    fb.new_check("Check all glyphs have codepoints assigned")
    failed = False
    for subtable in font['cmap'].tables:
      if subtable.isUnicode():
        for codepoint, name in subtable.cmap.items():
          if codepoint is None:
            failed = True
            fb.error(("Glyph {} lacks a unicode"
                      " codepoint assignment").format(codepoint))
    if not failed:
      fb.ok("All glyphs have a codepoint value assigned.")

    # ----------------------------------------------------
    fb.new_check("Check that glyph names do not exceed max length")
    failed = False
    for subtable in font['cmap'].tables:
      for codepoint, name in subtable.cmap.items():
        if len(name) > 109:
          failed = True
          fb.error(("Glyph name is too long:"
                    " '{}'").format(name))
    if not failed:
      fb.ok("No glyph names exceed max allowed length.")

    # -----------------------------------------------------
    fb.new_check("Monospace font has hhea.advanceWidthMax"
                 " equal to each glyph's advanceWidth ?")
    if monospace_detected:
      # hhea:advanceWidthMax is treated as source of truth here.
      max_advw = font['hhea'].advanceWidthMax
      outliers = 0
      for glyph_id in font['glyf'].glyphs:
        width = font['hmtx'].metrics[glyph_id][0]
        if width != max_advw:
          outliers += 1

      if outliers > 0:
        outliers_percentage = float(outliers) / len(font['glyf'].glyphs)
        fb.error(("This is a monospaced font, so advanceWidth"
                  " value should be the same across all glyphs,"
                  " but {} % of them have a different "
                  "value.").format(round(100 * outliers_percentage, 2)))
      else:
        fb.ok("hhea.advanceWidthMax is equal"
              " to all glyphs' advanceWidth in this monospaced font.")
    else:
      fb.skip("Skipping monospace-only check.")

##########################################################
## Metadata related checks:
##########################################################
    fontdir = os.path.dirname(font_file)
    metadata = os.path.join(fontdir, "METADATA.pb")
    if args.skip:
      # ignore METADATA.pb checks since user has requested that
      # we do not run googlefonts-specific checks
      pass
    elif not os.path.exists(metadata):
      logging.error("{} is missing a METADATA.pb file!".format(filename))
    else:
      family = get_FamilyProto_Message(metadata)
      fb.default_target = metadata

      # -----------------------------------------------------
      fb.new_check("METADATA.pb: Ensure designer simple short name.")
      if len(family.designer.split(' ')) >= 4 or\
         ' and ' in family.designer or\
         '.' in family.designer or\
         ',' in family.designer:
        fb.error('`designer` key must be simple short name')
      else:
        fb.ok('Designer is a simple short name')

      # -----------------------------------------------------
      fb.new_check("METADATA.pb: Fontfamily is listed"
                   " in Google Font Directory ?")
      url = ('http://fonts.googleapis.com'
             '/css?family=%s') % family.name.replace(' ', '+')
      try:
        fp = requests.get(url)
        if fp.status_code != 200:
          fb.error('No family found in GWF in %s' % url)
        else:
          fb.ok('Font is properly listed in Google Font Directory.')
      except:
        fb.warning("Failed to query GWF at {}".format(url))

      # -----------------------------------------------------
      fb.new_check("METADATA.pb: Designer exists in GWF profiles.csv ?")
      if family.designer == "":
        fb.error('METADATA.pb field "designer" MUST NOT be empty!')
      elif family.designer == "Multiple Designers":
        fb.skip("Found 'Multiple Designers' at METADATA.pb, which is OK,"
                "so we won't look for it at profiles.cvs")
      else:
        try:
          fp = urllib.urlopen(PROFILES_RAW_URL)
          designers = []
          for row in csv.reader(fp):
            if not row:
              continue
            designers.append(row[0].decode('utf-8'))
          if family.designer not in designers:
            fb.error(("METADATA.pb: Designer '{}' is not listed"
                      " in profiles.csv"
                      " (at '{}')").format(family.designer,
                                           PROFILES_GIT_URL))
          else:
            fb.ok(("Found designer '{}'"
                   " at profiles.csv").format(family.designer))
        except:
          fb.warning("Failed to fetch '{}'".format(PROFILES_RAW_URL))

      # -----------------------------------------------------
      fb.new_check("METADATA.pb: check if fonts field"
                   " only has unique 'full_name' values")
      fonts = {}
      for x in family.fonts:
        fonts[x.full_name] = x
      if len(set(fonts.keys())) != len(family.fonts):
        fb.error("Found duplicated 'full_name' values"
                 " in METADATA.pb fonts field")
      else:
        fb.ok("METADATA.pb 'fonts' field only has unique 'full_name' values")

      # -----------------------------------------------------
      fb.new_check("METADATA.pb: check if fonts field"
                   " only contains unique style:weight pairs")
      pairs = {}
      for f in family.fonts:
        styleweight = '%s:%s' % (f.style, f.weight)
        pairs[styleweight] = 1
      if len(set(pairs.keys())) != len(family.fonts):
        logging.error("Found duplicated style:weight pair"
                      " in METADATA.pb fonts field")
      else:
        fb.ok("METADATA.pb 'fonts' field only has unique style:weight pairs")

      # -----------------------------------------------------
      fb.new_check("METADATA.pb license is 'APACHE2', 'UFL' or 'OFL' ?")
      licenses = ['APACHE2', 'OFL', 'UFL']
      if family.license in licenses:
        fb.ok(("Font license is declared"
               " in METADATA.pb as '{}'").format(family.license))
      else:
        fb.error(("METADATA.pb license field ('{}')"
                  " must be one of the following: {}").format(
                    family.license,
                    licenses))

      # -----------------------------------------------------
      fb.new_check("METADATA.pb should contain at least"
                   " 'menu' and 'latin' subsets.")
      expected = list(sorted(family.subsets))

      missing = []
      for s in ["menu", "latin"]:
        if s not in list(family.subsets):
          missing.append(s)

      if missing != []:
        fb.error(("Subsets 'menu' and 'latin' are mandatory, but METADATA.pb"
                  " is missing '{}'").format(' and '.join(missing)))
      else:
        fb.ok("METADATA.pb contains 'menu' and 'latin' subsets.")

      # -----------------------------------------------------
      fb.new_check("METADATA.pb subsets should be alphabetically ordered.")
      expected = list(sorted(family.subsets))

      if list(family.subsets) != expected:
        fb.error(("METADATA.pb subsets are not sorted "
                  "in alphabetical order: Got ['{}']"
                  " and expected ['{}']").format("', '".join(family.subsets),
                                                 "', '".join(expected)))
      else:
        fb.ok("METADATA.pb subsets are sorted in alphabetical order")

      # -----------------------------------------------------
      fb.new_check("Copyright notice is the same in all fonts ?")
      copyright = ''
      fail = False
      for font_metadata in family.fonts:
        if copyright and font_metadata.copyright != copyright:
          fail = True
        copyright = font_metadata.copyright
      if fail:
        fb.error('METADATA.pb: Copyright field value'
                 ' is inconsistent across family')
      else:
        fb.ok('Copyright is consistent across family')

      # -----------------------------------------------------
      fb.new_check("Check that METADATA family values are all the same")
      name = ''
      fail = False
      for font_metadata in family.fonts:
        if name and font_metadata.name != name:
          fail = True
        name = font_metadata.name
      if fail:
        fb.error("METADATA.pb: Family name is not the same"
                 " in all metadata 'fonts' items.")
      else:
        fb.ok("METADATA.pb: Family name is the same"
              " in all metadata 'fonts' items.")

      # -----------------------------------------------------
      fb.new_check("According GWF standards font should have Regular style.")
      found = False
      for f in family.fonts:
        if f.weight == 400 and f.style == 'normal':
          found = True
      if found:
        fb.ok("Font has a Regular style.")
      else:
        fb.error("This font lacks a Regular"
                 " (style: normal and weight: 400)"
                 " as required by GWF standards.")

      # -------------------------------------------------------
      fb.new_check("Regular should be 400")
      if not found:
        fb.skip("This test will only run if font has a Regular style")
      else:
        badfonts = []
        for f in family.fonts:
          if f.full_name.endswith('Regular') and f.weight != 400:
            badfonts.append("{} (weight: {})".format(f.filename, f.weight))
        if len(badfonts) > 0:
          fb.error(('METADATA.pb: Regular font weight must be 400.'
                    ' Please fix: {}').format(', '.join(badfonts)))
        else:
          fb.ok('Regular has weight=400')
      # -----------------------------------------------------

      for f in family.fonts:
        if filename == f.filename:
          ###### Here go single-TTF metadata tests #######
          # ----------------------------------------------
          fb.new_check("Font on disk and in METADATA.pb"
                       " have the same family name ?")
          familynames = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if len(familynames) == 0:
            fb.error(("This font lacks a FONT_FAMILY_NAME entry"
                      " (nameID={}) in the name"
                      " table.").format(NAMEID_FONT_FAMILY_NAME))
          else:
            if f.name not in familynames:
              fb.error(('Unmatched family name in font:'
                        ' TTF has "{}" while METADATA.pb'
                        ' has "{}"').format(familynames, f.name))
            else:
              fb.ok(("Family name '{}' is identical"
                     " in METADATA.pb and on the"
                     " TTF file.").format(f.name))

          # -----------------------------------------------
          fb.new_check("Checks METADATA.pb 'postScriptName'"
                       " matches TTF 'postScriptName'")
          postscript_names = get_name_string(font, NAMEID_POSTSCRIPT_NAME)
          if len(postscript_names) == 0:
            fb.error(("This font lacks a POSTSCRIPT_NAME"
                      " entry (nameID={}) in the "
                      "name table.").format(NAMEID_POSTSCRIPT_NAME))
          else:
            postscript_name = postscript_names[0]

            if postscript_name != f.post_script_name:
              fb.error(('Unmatched postscript name in font:'
                        ' TTF has "{}" while METADATA.pb has'
                        ' "{}"').format(postscript_name,
                                        f.post_script_name))
            else:
              fb.ok(("Postscript name '{}' is identical"
                     " in METADATA.pb and on the"
                     " TTF file.").format(f.post_script_name))

          # -----------------------------------------------
          fb.new_check("METADATA.pb 'fullname' value"
                       " matches internal 'fullname' ?")
          full_fontnames = get_name_string(font, NAMEID_FULL_FONT_NAME)
          if len(full_fontnames) == 0:
            fb.error(("This font lacks a FULL_FONT_NAME"
                      " entry (nameID={}) in the "
                      "name table.").format(NAMEID_FULL_FONT_NAME))
          else:
            full_fontname = full_fontnames[0]

            if full_fontname != f.full_name:
              fb.error(('Unmatched fullname in font:'
                        ' TTF has "{}" while METADATA.pb'
                        ' has "{}"').format(full_fontname, f.full_name))
            else:
              fb.ok(("Full fontname '{}' is identical"
                     " in METADATA.pb and on the "
                     "TTF file.").format(full_fontname))

          # -----------------------------------------------
          fb.new_check("METADATA.pb fonts 'name' property"
                       " should be same as font familyname")
          font_familynames = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if len(font_familynames) == 0:
            fb.error(("This font lacks a FONT_FAMILY_NAME entry"
                      " (nameID={}) in the "
                      "name table.").format(NAMEID_FONT_FAMILY_NAME))
          else:
            font_familyname = font_familynames[0]

            if font_familyname not in f.name:
              fb.error(('Unmatched familyname in font:'
                        ' TTF has "{}" while METADATA.pb has'
                        ' name="{}"').format(familyname, f.name))
            else:
              fb.ok(("OK: Family name '{}' is identical"
                     " in METADATA.pb and on the"
                     " TTF file.").format(f.name))

          # -----------------------------------------------
          fb.new_check("METADATA.pb 'fullName' matches 'postScriptName' ?")
          regex = re.compile(r'\W')
          post_script_name = regex.sub('', f.post_script_name)
          fullname = regex.sub('', f.full_name)
          if fullname != post_script_name:
            fb.error(('METADATA.pb full_name="{0}"'
                      ' does not match post_script_name ='
                      ' "{1}"').format(f.full_name,
                                       f.post_script_name))
          else:
            fb.ok("METADATA.pb fields 'fullName' and"
                  " 'postScriptName' have the same value.")

          # -----------------------------------------------
          fb.new_check("METADATA.pb 'filename' matches 'postScriptName' ?")
          regex = re.compile(r'\W')
          post_script_name = regex.sub('', f.post_script_name)
          filename = regex.sub('', os.path.splitext(f.filename)[0])
          if filename != post_script_name:
            msg = ('METADATA.pb filename="{0}" does not match '
                   'post_script_name="{1}."')
            fb.error(msg.format(f.filename, f.post_script_name))
          else:
            fb.ok("METADATA.pb fields 'filename' and"
                  " 'postScriptName' have matching values.")

          # -----------------------------------------------
          fb.new_check("METADATA.pb 'name' contains font name"
                       " in right format ?")
          font_familynames = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if len(font_familynames) == 0:
            logging.skip("A corrupt font that lacks a font_family"
                         " nameID entry caused a whole sequence"
                         " of tests to be skipped.")
          else:
            font_familyname = font_familynames[0]

            if font_familyname in f.name:
              fb.ok("METADATA.pb 'name' contains font name"
                    " in right format.")
            else:
              fb.error(("METADATA.pb name='{}' does not match"
                        " correct font name format.").format(f.name))
            # -----------

            fb.new_check("METADATA.pb 'full_name' contains"
                         " font name in right format ?")
            if font_familyname in f.name:
              fb.ok("METADATA.pb 'full_name' contains"
                    " font name in right format.")
            else:
              fb.error(("METADATA.pb full_name='{}' does not match"
                        " correct font name format.").format(f.full_name))
            # -----------

            fb.new_check("METADATA.pb 'filename' contains"
                         " font name in right format ?")
            if "".join(str(font_familyname).split()) in f.filename:
              fb.ok("METADATA.pb 'filename' contains"
                    " font name in right format.")
            else:
              fb.error(("METADATA.pb filename='{}' does not match"
                        " correct font name format.").format(f.filename))
            # -----------

            fb.new_check("METADATA.pb 'postScriptName' contains"
                         " font name in right format ?")
            if "".join(str(font_familyname).split()) in f.post_script_name:
              fb.ok("METADATA.pb 'postScriptName' contains"
                    " font name in right format ?")
            else:
              fb.error(("METADATA.pb postScriptName='{}'"
                        " does not match correct"
                        " font name format.").format(f.post_script_name))

          # -----------------------------------------------
          fb.new_check("Copyright notice matches canonical pattern?")
          almost_matches = re.search(r'(Copyright\s+20\d{2}.+)',
                                     f.copyright)
          does_match = re.search(r'(Copyright\s+20\d{2}\s+.*\(.+@.+\..+\))',
                                 f.copyright)
          if (does_match is not None):
            fb.ok("METADATA.pb copyright field matches canonical pattern.")
          else:
            if (almost_matches):
              fb.warning(("METADATA.pb: Copyright notice is okay,"
                          " but it lacks an email address."
                          " Expected pattern is:"
                          " 'Copyright 2016 Author Name (name@site.com)'\n"
                          "But detected copyright string is:"
                          " '{}'").format(f.copyright))
            else:
              fb.error(("METADATA.pb: Copyright notices should match"
                        " the folowing pattern:"
                        " 'Copyright 2016 Author Name (name@site.com)'\n"
                        "But instead we have got: '{}'").format(f.copyright))

          # -----------------------------------------------
          fb.new_check("Copyright notice does not contain Reserved Font Name")
          if 'Reserved Font Name' in f.copyright:
            fb.error(('METADATA.pb: copyright field ("%s")'
                      ' contains "Reserved Font Name"') % f.copyright)
          else:
            fb.ok('METADATA.pb copyright field'
                  ' does not contain "Reserved Font Name"')

          # -----------------------------------------------
          fb.new_check("Copyright notice shouldn't exceed 500 chars")
          if len(f.copyright) > 500:
            fb.error("METADATA.pb: Copyright notice exceeds"
                     " maximum allowed lengh of 500 characteres.")
          else:
            fb.ok("Copyright notice string is"
                  " shorter than 500 chars.")

          # -----------------------------------------------
          fb.new_check("Filename is set canonically?")

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
            fb.error("METADATA.pb: filename field ('{}')"
                     " does not match"
                     " canonical name '{}'".format(f.filename,
                                                   canonical_filename))
          else:
            fb.ok('Filename is set canonically.')

          # -----------------------------------------------
          fb.new_check("METADATA.pb font.style `italic`"
                       " matches font internals?")
          if f.style != 'italic':
            fb.skip("This test only applies to italic fonts.")
          else:
            font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
            font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
            if len(font_familyname) == 0 or len(font_fullname) == 0:
              fb.skip("Font lacks familyname and/or"
                      " fullname entries in name table.")
              # these fail scenarios were already tested above
              # (passing those previous tests is a prerequisite for this one)
            else:
              font_familyname = font_familyname[0]
              font_fullname = font_fullname[0]

              if not bool(font['head'].macStyle & MACSTYLE_ITALIC):
                  fb.error('METADATA.pb style has been set to italic'
                           ' but font macStyle is improperly set')
              elif not font_familyname.split('-')[-1].endswith('Italic'):
                  fb.error(('Font macStyle Italic bit is set'
                            ' but nameID %d ("%s")'
                            ' is not ended '
                            'with "Italic"') % (NAMEID_FONT_FAMILY_NAME,
                                                font_familyname))
              elif not font_fullname.split('-')[-1].endswith('Italic'):
                  fb.error(('Font macStyle Italic bit is set'
                            ' but nameID %d ("%s")'
                            ' is not ended'
                            ' with "Italic"') % (NAMEID_FULL_FONT_NAME,
                                                 font_fullname))
              else:
                fb.ok("OK: METADATA.pb font.style 'italic'"
                      " matches font internals.")

          # -----------------------------------------------
          fb.new_check("METADATA.pb font.style `normal`"
                       " matches font internals?")
          if f.style != 'normal':
            fb.skip("This test only applies to normal fonts.")
          else:
            font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
            font_fullname = get_name_string(font, NAMEID_FULL_FONT_NAME)
            if len(font_familyname) == 0 or len(font_fullname) == 0:
              fb.skip("Font lacks familyname and/or"
                      " fullname entries in name table.")
              # these fail scenarios were already tested above
              # (passing those previous tests is a prerequisite for this one)
            else:
              font_familyname = font_familyname[0]
              font_fullname = font_fullname[0]

              if bool(font['head'].macStyle & MACSTYLE_ITALIC):
                  fb.error('METADATA.pb style has been set to normal'
                           ' but font macStyle is improperly set')
              elif font_familyname.split('-')[-1].endswith('Italic'):
                  fb.error(('Font macStyle indicates a non-Italic font,'
                            ' but nameID %d (FONT_FAMILY_NAME: "%s") ends'
                            ' with "Italic"').format(NAMEID_FONT_FAMILY_NAME,
                                                     font_familyname))
              elif font_fullname.split('-')[-1].endswith('Italic'):
                  fb.error('Font macStyle indicates a non-Italic font'
                           ' but nameID %d (FULL_FONT_NAME: "%s") ends'
                           ' with "Italic"'.format(NAMEID_FULL_FONT_NAME,
                                                   font_fullname))
              else:
                fb.ok("METADATA.pb font.style 'normal'"
                      " matches font internals.")

              # ----------
              fb.new_check("Metadata key-value match to table name fields?")
              if font_familyname != f.name:
                fb.error(("METADATA.pb Family name '{}')"
                          " does not match name table"
                          " entry '{}' !").format(f.name,
                                                  font_familyname))
              elif font_fullname != f.full_name:
                fb.error(("METADATA.pb: Fullname ('{}')"
                          " does not match name table"
                          " entry '{}' !").format(f.full_name,
                                                  font_fullname))
              else:
                fb.ok("METADATA.pb familyname and fullName fields"
                      " match corresponding name table entries.")

          # -----------------------------------------------
          fb.new_check("Check if fontname is not camel cased.")
          if bool(re.match(r'([A-Z][a-z]+){2,}', f.name)):
            fb.error(("METADATA.pb: '%s' is a CamelCased name."
                      " To solve this, simply use spaces"
                      " instead in the font name.").format(f.name))
          else:
            fb.ok("Font name is not camel-cased.")

          # -----------------------------------------------
          fb.new_check("Check font name is the same as family name.")
          if f.name != family.name:
            fb.error(('METADATA.pb: %s: Family name "%s"'
                      ' does not match'
                      ' font name: "%s"').format(f.filename,
                                                 family.name,
                                                 f.name))
          else:
            fb.ok('Font name is the same as family name.')

          # -----------------------------------------------
          fb.new_check("Check that font weight has a canonical value")
          first_digit = f.weight / 100
          if (f.weight % 100) != 0 or (first_digit < 1 or first_digit > 9):
            fb.error(("METADATA.pb: The weight is declared"
                      " as {} which is not a "
                      "multiple of 100"
                      " between 100 and 900.").format(f.weight))
          else:
            fb.ok("Font weight has a canonical value.")

          # -----------------------------------------------
          fb.new_check("Checking OS/2 usWeightClass"
                       " matches weight specified at METADATA.pb")
          assert_table_entry('OS/2', 'usWeightClass', f.weight)
          log_results("OS/2 usWeightClass matches "
                      "weight specified at METADATA.pb")

          # -----------------------------------------------
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
          # -----------------------------------------------
          fb.new_check("Metadata weight matches postScriptName")
          pair = []
          for k, weight in weights.items():
            if weight == f.weight:
              pair.append((k, weight))

          if not pair:
            fb.error('METADATA.pb: Font weight'
                     ' does not match postScriptName')
          elif not (f.post_script_name.endswith('-' + pair[0][0]) or
                    f.post_script_name.endswith('-%s' % pair[1][0])):
            fb.error('METADATA.pb: postScriptName ("{}")'
                     ' with weight {} must be '.format(f.post_script_name,
                                                       pair[0][1]) +
                     'ended with "{}" or "{}"'.format(pair[0][0],
                                                      pair[1][0]))
          else:
            fb.ok("Weight value matches postScriptName.")

          # -----------------------------------------------
          fb.new_check("METADATA.pb lists fonts named canonicaly?")
          font_familyname = get_name_string(font, NAMEID_FONT_FAMILY_NAME)
          if len(font_familyname) == 0:
            fb.skip("Skipping this test due to the lack"
                    " of a FONT_FAMILY_NAME in the name table.")
          else:
            font_familyname = font_familyname[0]

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
              fb.ok("METADATA.pb lists fonts named canonicaly.")
            else:
              v = map(lambda x: font_familyname + ' ' + x, _weights)
              fb.error('Canonical name in font expected:'
                       ' [%s] but %s' % (v, f.full_name))

          # ----------------------------------------------
          fb.new_check("Font styles are named canonically?")

          def find_italic_in_name_table():
            for entry in font['name'].names:
              if 'italic' in entry.string.decode(entry.getEncoding()).lower():
                return True
            return False

          def is_italic():
            return (font['head'].macStyle & MACSTYLE_ITALIC or
                    font['post'].italicAngle or
                    find_italic_in_name_table())

          if f.style not in ['italic', 'normal']:
            fb.skip("This check only applies to font styles declared"
                    " as 'italic' or 'regular' on METADATA.pb")
          else:
            if is_italic() and f.style != 'italic':
              fb.error("The font style is %s"
                       " but it should be italic" % (f.style))
            elif not is_italic() and f.style != 'normal':
              fb.error(("The font style is %s"
                        " but it should be normal") % (f.style))
            else:
              fb.ok("Font styles are named canonically")

          # ---------------------------------------------
          ###### End of single-TTF metadata tests #######

    # ----------------------------------------------------
    # https://github.com/googlefonts/fontbakery/issues/971
    # DC: Each fix line should set a fix flag, and
    # if that flag is True by this point, only then write the file
    # and then say any further output regards fixed files, and
    # re-run the script on each fixed file with logging level = error
    # so no info-level log items are shown
    font_file_output = os.path.splitext(filename)[0] + ".fix"
    if args.autofix:
      font.save(font_file_output)
      logging.info("{} saved\n".format(font_file_output))
    font.close()

    fb.output_report(font_file)
    fb.reset_report()

  # -------------------------------------------------------
  if not args.verbose and \
     not args.json and \
     not args.ghm and \
     not args.error:
    # in this specific case, the user would have no way to see
    # the actual check results. So here we inform the user
    # that at least one of these command line parameters
    # needs to be used in order to see the details.
    print ("In order to see the actual check result messages,\n"
           "use one of the following command-line parameters:\n"
           "  --verbose\tOutput results to stdout.\n"
           "  --json \tSave results to a file in JSON format.\n"
           "  --ghm  \tSave results to a file in GitHub Markdown format.\n"
           "  --error\tPrint only the error messages (outputs to stderr).\n")

  if len(json_report_files) > 0:
    print(("Saved check results in "
           "JSON format to:\n\t{}"
           "").format('\n\t'.join(json_report_files)))
  if len(ghm_report_files) > 0:
    print(("Saved check results in "
           "GitHub Markdown format to:\n\t{}"
           "").format('\n\t'.join(ghm_report_files)))

__author__ = "The Font Bakery Authors"
if __name__ == '__main__':
  main()
