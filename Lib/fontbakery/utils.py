#!/usr/bin/env python3
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

from fontTools.ttLib import TTFont
from typing import Text, Optional

def text_flow(content, width=80, indent=0, left_margin=0,
              space_padding=False, text_color="{}".format):
  result = ""
  for line in content.split("\n"):
    if line.strip() == "":
      if space_padding:
        result += " " * indent + text_color(" " * width)
      result += "\n"
      continue

    words = line.split(" ")
    while words:
      this_line = " " * left_margin + words.pop(0)

      if len(this_line) > width:
        # let's see what we can do to make it fit
        if "/" in this_line:
          # here we feed-back chunks of a URL
          # into words if it overflows the block
          chunks = this_line.split('/')
          new_line = chunks.pop(0)
          while chunks:
            if len(new_line) + 1 + len(chunks[0]) >= width: break
            new_line += "/" + chunks.pop(0)
          this_line = new_line
          words.insert(0, "/" + "/".join(chunks))
        else:
          # not sure what else to do,
          # so we'll simply cut the long word
          words.insert(0, this_line[width:])
          this_line = this_line[:width]

      while words and (len(this_line) + 1 + len(words[0]) < width or
                       len(words[0]) >= width):
        this_line += " " + words.pop(0)

      if space_padding:
        # pad the line with spaces to fit the block width:
        this_line += " " * (width - len(this_line))
      result += " " * indent + text_color(this_line) + "\n"
  return result


def unindent_rationale(rationale, checkid=None):
  content = ""
  for line in rationale.split("\n"):
    if line.strip() == "":
      content += "\n"
      continue

    if checkid and line[:4].strip() != "":
      import sys
      sys.exit(f"FATAL ERROR: The rationale metadata on '{checkid}' must be indented by 4 spaces!")

    # all lines are assumed to be indented by 4 spaces
    content += line[4:] + "\n"
  return content


def split_camel_case(camelcase):
  result = []
  word = ""
  for char in camelcase:
    if char.isupper():
      if word != "":
        result.append(word)
      word = char
    else:
      word += char

  if word != "":
    result.append(word)
  return " ".join(result)


def suffix(font):
  filename = os.path.basename(font)
  basename = os.path.splitext(filename)[0]
  s = basename.split('-')
  s.pop(0)
  return '-'.join(s)


def portable_path(p):
  return os.path.join(*p.split('/'))


def TEST_FILE(f):
  return portable_path("data/test/" + f)


def pretty_print_list(values, shorten=10, sep=", ", glue="and"):
  if len(values) == 1:
    return str(values[0])

  if shorten and len(values) > shorten + 2:
    return "{} {} {} more.".format(sep.join(map(str, values[:shorten])),
                                   glue,
                                   len(values) - shorten)
  else:
    return "{} {} {}".format(sep.join(map(str, values[:-1])),
                             glue,
                             str(values[-1]))


def get_regular(fonts):
  # TODO: Maybe also support getting a regular instance from a variable font?
  for font in fonts:
    if "-Regular.ttf" in font:
      return font


def get_absolute_path(p):
  if os.path.isabs(p):
    abspath = p
  else:
    abspath = os.path.join(os.path.abspath('.'), p)
  return abspath


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


def get_name_entries(font,
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
      results.append(entry)
  return results


def get_name_entry_strings(font,
                           nameID,
                           platformID=None,
                           encodingID=None,
                           langID=None):
  entries = get_name_entries(font, nameID, platformID, encodingID, langID)
  return list(map(lambda e: e.string.decode(e.getEncoding()), entries))


def name_entry_id(name):
  from fontbakery.constants import (NameID,
                                    PlatformID)
  return "[{}({}):{}({})]".format(NameID(name.nameID).name,
                                  name.nameID,
                                  PlatformID(name.platformID).name,
                                  name.platformID)


def get_glyph_name(font: TTFont, codepoint: int) -> Optional[str]:
  next_best_cmap = font.getBestCmap()

  if codepoint in next_best_cmap:
    return next_best_cmap[codepoint]

  return None


def glyph_contour_count(font, name):
    """Contour count for specified glyph.
    This implementation will also return contour count for
    composite glyphs.
    """
    contour_count = 0
    items = [font['glyf'][name]]

    while items:
        g = items.pop(0)
        if g.isComposite():
            for comp in g.components:
                if comp.glyphName != ".ttfautohint":
                    items.append(font['glyf'][comp.glyphName])
        if g.numberOfContours != -1:
            contour_count += g.numberOfContours
    return contour_count


def get_font_glyph_data(font):
    """Return information for each glyph in a font"""
    from fontbakery.constants import (PlatformID,
                                      WindowsEncodingID)
    font_data = []

    try:
        subtable = font['cmap'].getcmap(PlatformID.WINDOWS,
                                        WindowsEncodingID.UNICODE_BMP)
        if not subtable:
          # Well... Give it a chance here...
          # It may be using a different Encoding_ID value
          subtable = font['cmap'].tables[0]

        cmap = subtable.cmap
    except:
        return None

    cmap_reversed = dict(zip(cmap.values(), cmap.keys()))

    for glyph_name in font.getGlyphSet().keys():
        if glyph_name in cmap_reversed:
            uni_glyph = cmap_reversed[glyph_name]
            contours = glyph_contour_count(font, glyph_name)
            font_data.append({
                'unicode': uni_glyph,
                'name': glyph_name,
                'contours': {contours}
            })
    return font_data


def get_FamilyProto_Message(path):
  from fontbakery.fonts_public_pb2 import FamilyProto
  from google.protobuf import text_format
  message = FamilyProto()
  text_data = open(path, "rb").read()
  text_format.Merge(text_data, message)
  return message


def check_bit_entry(ttFont, table, attr, expected, bitmask, bitname):
  from fontbakery.message import Message
  from fontbakery.checkrunner import (PASS, FAIL)
  value = getattr(ttFont[table], attr)
  name_str = f"{table} {attr} {bitname} bit"
  if bool(value & bitmask) == expected:
    return PASS, f"{name_str} is properly set."
  else:
    if expected:
      expected_str = "set"
    else:
      expected_str = "unset"
    return FAIL, Message(f"bad-{bitname}",
                         f"{name_str} should be {expected_str}.")


class BadCertificateSetupException(Exception):
    pass


def download_file(url):
  from urllib.request import urlopen
  from urllib.error import URLError
  from io import BytesIO
  try:
    return BytesIO(urlopen(url).read())
  except URLError as e:
    if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
      raise BadCertificateSetupException("You probably installed official"
            " Mac python from python.org but forgot to also install"
            " the certificates. There is a note in the installer"
            " Readme about that. Check the Python folder in the"
            " Applications directory, you should find a shell script"
            " to install the certificates.")


def cff_glyph_has_ink(font: TTFont, glyph_name: Text) -> bool:
  if 'CFF2' in font:
    top_dict = font['CFF2'].cff.topDictIndex[0]
  else:
    top_dict = font['CFF '].cff.topDictIndex[0]
  char_strings = top_dict.CharStrings
  char_string = char_strings[glyph_name]
  bounds = char_string.calcBounds(char_strings)
  if bounds is not None:
    return True

  return False


def ttf_glyph_has_ink(font: TTFont, name: Text) -> bool:
  glyph = font['glyf'].glyphs[name]
  glyph.expand(font['glyf'])

  if not glyph.isComposite():
    if glyph.numberOfContours == 0:
      return False
    (coords, _, _) = glyph.getCoordinates(font['glyf'])
    # you need at least 3 points to draw
    return len(coords) > 2

  # Check for ink in each sub-component.
  for glyph_name in glyph.getComponentNames(glyph.components):
    if glyph_has_ink(font, glyph_name):
      return True

  return False


def unicoderange_bit_name(bit):
  from fontbakery.constants import UNICODERANGE_DATA
  return UNICODERANGE_DATA[bit][0][1]


def get_preferred_cmap(ttFont):
  cmaps = {}
  for table in ttFont["cmap"].tables:
    cmaps[table.format] = table.cmap

  if 12 in cmaps:
    return cmaps[12]

  elif 4 in cmaps:
    return cmaps[4]

  else:
    return None


def chars_in_range(ttFont, bit):
  from fontbakery.constants import UNICODERANGE_DATA
  cmap = get_preferred_cmap(ttFont)
  chars = []
  for c in sorted(cmap):
    for entry in UNICODERANGE_DATA[bit]:
      if c >= entry[2] and c <= entry[3]:
        chars.append(c)
  return chars


def compute_unicoderange_bits(ttFont):
  from fontbakery.constants import UNICODERANGE_DATA
  cmap = get_preferred_cmap(ttFont)
  result = 0
  for c in sorted(cmap):
    for bit in range(len(UNICODERANGE_DATA)):
      for entry in UNICODERANGE_DATA[bit]:
        bit = entry[0]
        if c >= entry[2] and c <= entry[3]:
          result |= (1 << bit)
  return result


def glyph_has_ink(font: TTFont, name: Text) -> bool:
  """Checks if specified glyph has any ink.

  That is, that it has at least one defined contour associated.
  Composites are considered to have ink if any of their components have ink.
  Args:
      font:       the font
      glyph_name: The name of the glyph to check for ink.
  Returns:
      True if the font has at least one contour associated with it.
  """
  if 'glyf' in font:
    return ttf_glyph_has_ink(font, name)
  elif ('CFF ' in font) or ('CFF2' in font):
    return cff_glyph_has_ink(font, name)
  else:
    raise Exception("Could not find 'glyf', 'CFF ', or 'CFF2' table.")


def assert_results_contain(check_results, expected_status, expected_msgcode=None):
  """
  This helper function is useful when we want to make sure that
  a certain log message is emited by a check but it can be in any
  order among other log messages.
  """
  found = False
  check_results = list(check_results)
  for status, message in check_results:
    if status == expected_status and message.code == expected_msgcode:
      found = True
      break
  if not found:
    print(f"Expected to find {expected_status}, [code: {expected_msgcode}]\n"
          f"But did not find it in:\n"
          f"{check_results}")
  assert(found)


def filenames_ending_in(suffix, root):
  '''
  Returns a list of the filenames of all files in a given directory subtree
  that have the given filename suffix. Example: List all ".json" files.
  '''
  filenames = []
  for f in os.listdir(root):
    fullpath = os.path.join(root, f)
    if f.endswith(suffix):
      filenames.append(fullpath)
    if os.path.isdir(fullpath):
      filenames.extend(filenames_ending_in(suffix, fullpath))
  return filenames
