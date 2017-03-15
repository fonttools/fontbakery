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
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from constants import PLATFORM_ID_WINDOWS,\
                      PLAT_ENC_ID_UCS2,\
                      PLAT_ENC_ID_UCS4
from fontTools import ttLib
from fontTools.pens.areaPen import AreaPen
from StringIO import StringIO
from TargetFont import TargetFont
from urllib import urlopen
from zipfile import ZipFile
import tempfile

# =====================================
# HELPER FUNCTIONS


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


def parse_version_string(fb, s):
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
    try:
      from fonts_public_pb2 import FamilyProto
      from google.protobuf import text_format
      message = FamilyProto()
      text_data = open(path, "rb").read()
      text_format.Merge(text_data, message)
      return message
    except:
      sys.exit("Needs protobuf.\n\nsudo pip install protobuf")


def save_FamilyProto_Message(path, message):
    try:
      from google.protobuf import text_format
      open(path, "wb").write(text_format.MessageToString(message))
    except:
      sys.exit("Needs protobuf.\n\nsudo pip install protobuf")


def fetch_vendorID_list(logging):
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
  return registered_vendor_ids


def font_key(f):
  return "{}-{}-{}".format(f.filename,
                           f.post_script_name,
                           f.weight)


def version_is_newer(a, b):
  a = map(int, a.split("."))
  b = map(int, b.split("."))
  return a > b


def check_bit_entry(fb, font, table, attr, expected, bitmask, bitname):
  value = getattr(font[table], attr)
  name_str = "{} {} {} bit".format(table, attr, bitname)
  if bool(value & bitmask) == expected:
    fb.ok("{} is properly set.".format(name_str))
  else:
    if expected:
      expected_str = "set"
    else:
      expected_str = "reset"
    if fb.config['autofix']:
      fb.hotfix("{} has been {}.".format(name_str, expected_str))
      if expected:
        setattr(font[table], attr, value | bitmask)
      else:
        setattr(font[table], attr, value & ~bitmask)
    else:
      fb.error("{} should be {}.".format(name_str, expected_str))


def download_family_from_GoogleFontDirectory(family_name):
    """Return a zipfile containing a font family hosted on fonts.google.com"""
    url_prefix = 'https://fonts.google.com/download?family='
    url = '%s%s' % (url_prefix, family_name.replace(' ', '+'))
    request = urlopen(url)
    # print(request.text)
    return ZipFile(StringIO(request.read()))


def fonts_from_zip(zipfile):
  '''return a list of fontTools TTFonts'''
  fonts = []
  for file_name in zipfile.namelist():
    if file_name.endswith(".ttf"):
      font = TargetFont(ttLib.TTFont(zipfile.open(file_name)))
      font.fullpath = file_name
      fonts.append(font)
  return fonts


def glyphs_surface_area(font):
  """Calculate the surface area of a glyph's ink"""
  glyphs = {}
  glyph_set = font.getGlyphSet()
  area_pen = AreaPen(glyph_set)

  for glyph in glyph_set.keys():
    glyph_set[glyph].draw(area_pen)

    area = area_pen.value
    area_pen.value = 0
    glyphs[glyph] = area
  return glyphs


def ttfauto_fpgm_xheight_rounding(fpgm_tbl):
  """Find the value from the fpgm table which controls ttfautohint's
  increase xheight parameter, '--increase-x-height'.
  This implementation is based on ttfautohint v1.6.

  This function has been tested on every font in the fonts/google repo
  which has an fpgm table. Results have been stored in a spreadsheet:
  http://tinyurl.com/jmlfmh3

  For more information regarding the fpgm table read:
  http://tinyurl.com/jzekfyx"""
  fpgm_tbl = '\n'.join(fpgm_tbl)
  xheight_pattern = r'(MPPEM\[ \].*\nPUSHW\[ \].*\n)([0-9]{1,5})'
  try:
    xheight_val = int(re.search(xheight_pattern, fpgm_tbl).group(2))
  except AttributeError:
    # No instruction for xheight rounding exists
    xheight_val = None
  return xheight_val
