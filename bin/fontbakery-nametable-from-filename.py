#!/usr/bin/env python
# Copyright 2013,2016 The Font Bakery Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import re
import ntpath
import argparse
from argparse import RawTextHelpFormatter
from fontTools.ttLib import TTFont, newTable


description = """

fontbakery-nametable-from-filename.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replace a collection of fonts nametable's with new tables based on the Google
Fonts naming spec from just the filename.

The fsSelection, fsType and macStyle also get updated to reflect the new
names.
"""

WIN_SAFE_STYLES = [
  'Regular',
  'Bold',
  'Italic',
  'BoldItalic',
]

MACSTYLE = {
  'Regular': 0,
  'Bold': 1,
  'Italic': 2,
  'Bold Italic': 3
}

# Weight name to value mapping:
WEIGHTS = {
  "Thin": 250,
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

REQUIRED_FIELDS = [
  (0, 1, 0, 0),
  (1, 1, 0, 0),
  (2, 1, 0, 0),
  (3, 1, 0, 0),
  (4, 1, 0, 0),
  (5, 1, 0, 0),
  (6, 1, 0, 0),
  (7, 1, 0, 0),
  (8, 1, 0, 0),
  (9, 1, 0, 0),
  (11, 1, 0, 0),
  (12, 1, 0, 0),
  (13, 1, 0, 0),
  (14, 1, 0, 0),
  (0, 3, 1, 1033),
  (1, 3, 1, 1033),
  (1, 3, 1, 1033),
  (2, 3, 1, 1033),
  (3, 3, 1, 1033),
  (4, 3, 1, 1033),
  (5, 3, 1, 1033),
  (6, 3, 1, 1033),
  (7, 3, 1, 1033),
  (8, 3, 1, 1033),
  (9, 3, 1, 1033),
  (11, 3, 1, 1033),
  (12, 3, 1, 1033),
  (13, 3, 1, 1033),
  (14, 3, 1, 1033),
]


def _split_camelcase(text):
  return re.sub(r"(?<=\w)([A-Z])", r" \1", text)


def _mac_subfamily_name(style_name):
  if style_name.startswith('Italic'):
    pass
  elif 'Italic' in style_name:
    style_name = style_name.replace('Italic', ' Italic')
  return style_name


def _unique_id(version, vendor_id, filename):
  # Glyphsapp style 2.000;MYFO;Arsenal-Bold
  # version;vendorID;filename
  return '%s;%s;%s' % (version, vendor_id, filename)


def _version(text):
  return re.search(r'[0-9]{1,4}\.[0-9]{1,8}', text).group(0)


def _full_name(family_name, style_name):
  style_name = _mac_subfamily_name(style_name)
  full_name = '%s %s' % (family_name, style_name)
  return full_name


def _win_family_name(family_name, style_name):
  name = family_name
  if style_name not in WIN_SAFE_STYLES:
    name = '%s %s' % (family_name, style_name)
  if 'Italic' in name:
    name = re.sub(r'Italic', r'', name)
  return name


def _win_subfamily_name(style_name):
  name = style_name
  if 'BoldItalic' == name:
    return 'Bold Italic'
  elif 'Italic' in name:
    return 'Italic'
  elif name == 'Bold':
    return 'Bold'
  else:
    return 'Regular'


def set_usWeightClass(style_name):
  name = style_name
  if name != 'Italic':
    name = re.sub(r'Italic', r'', style_name)
  return WEIGHTS[name]


def set_macStyle(style_name):
    return MACSTYLE[style_name]


def set_fsSelection(fsSelection, style):
  bits = fsSelection
  if 'Regular' in style:
    bits |= 0b1000000
  else:
    bits &= ~0b1000000

  if style in ['Bold', 'BoldItalic']:
    bits |= 0b100000
  else:
    bits &= ~0b100000

  if 'Italic' in style:
    bits |= 0b1
  else:
    bits &= ~0b1

  if not bits:
    bits = 0b1000000

  return bits


def nametable_from_filename(filepath):
  """Generate a new nametable based on a ttf and the GF Spec"""
  font = TTFont(filepath)
  old_table = font['name']
  new_table = newTable('name')
  filename = ntpath.basename(filepath)[:-4]

  family_name, style_name = filename.split('-')
  family_name = _split_camelcase(family_name)

  font_version = font['name'].getName(5, 3, 1, 1033)
  font_version = str(font_version).decode('utf_16_be')
  vendor_id = font['OS/2'].achVendID

  # SET MAC NAME FIELDS
  # -------------------
  # Copyright
  old_cp = old_table.getName(0, 3, 1, 1033).string.decode('utf_16_be')
  new_table.setName(old_cp.encode('mac_roman'), 0, 1, 0, 0)
  # Font Family Name
  new_table.setName(family_name.encode('mac_roman'), 1, 1, 0, 0)
  # Subfamily name
  mac_subfamily_name = _mac_subfamily_name(style_name).encode('mac_roman')
  new_table.setName(mac_subfamily_name, 2, 1, 0, 0)
  # Unique ID
  unique_id = _unique_id(_version(font_version), vendor_id, filename)
  mac_unique_id = unique_id.encode('mac_roman')
  new_table.setName(mac_unique_id, 3, 1, 0, 0)
  # Full name
  fullname = _full_name(family_name, style_name)
  mac_fullname = fullname.encode('mac_roman')
  new_table.setName(mac_fullname, 4, 1, 0, 0)
  # Version string
  old_v = old_table.getName(5, 3, 1, 1033).string.decode('utf_16_be')
  mac_old_v = old_v.encode('mac_roman')
  new_table.setName(mac_old_v, 5, 1, 0, 0)
  # Postscript name
  mac_ps_name = filename.encode('mac_roman')
  new_table.setName(mac_ps_name, 6, 1, 0, 0)

  # SET WIN NAME FIELDS
  # -------------------
  # Copyright
  new_table.setName(old_cp, 0, 3, 1, 1033)
  # Font Family Name
  win_family_name = _win_family_name(family_name, style_name)
  win_family_name = win_family_name.encode('utf_16_be')
  new_table.setName(win_family_name, 1, 3, 1, 1033)
  # Subfamily Name
  win_subfamily_name = _win_subfamily_name(style_name).encode('utf_16_be')
  new_table.setName(win_subfamily_name, 2, 3, 1, 1033)
  # Unique ID
  win_unique_id = unique_id.encode('utf_16_be')
  new_table.setName(win_unique_id, 3, 3, 1, 1033)
  # Full name
  win_fullname = fullname.encode('utf_16_be')
  new_table.setName(win_fullname, 4, 3, 1, 1033)
  # Version string
  win_old_v = old_v.encode('utf_16_be')
  new_table.setName(win_old_v, 5, 3, 1, 1033)
  # Postscript name
  win_ps_name = filename.encode('utf_16_be')
  new_table.setName(win_ps_name, 6, 3, 1, 1033)

  if style_name not in WIN_SAFE_STYLES:
    # Preferred Family Name
    new_table.setName(family_name.encode('utf_16_be'), 16, 3, 1, 1033)
    # Preferred SubfamilyName
    win_pref_subfam_name = _mac_subfamily_name(style_name).encode('utf_16_be')
    new_table.setName(win_pref_subfam_name, 17, 3, 1, 1033)

  # PAD missing fields
  # ------------------
  for field in REQUIRED_FIELDS:
    text = None
    if new_table.getName(*field):
      pass  # Name has already been updated
    elif old_table.getName(*field):
      text = old_table.getName(*field).string
    elif old_table.getName(field[0], 3, 1, 1033):
      text = old_table.getName(field[0], 3, 1, 1033).string.decode('utf_16_be')
    elif old_table.getName(field[0], 1, 0, 0):  # check if field exists for mac
      text = old_table.getName(field[0], 3, 1, 1033).string.decode('mac_roman')

    if text:
      enc = 'utf_16_be' if field[0] == 3 else 'mac_roman'
      new_table.setName(text.encode(enc), *field)
  return new_table


parser = argparse.ArgumentParser(description=description,
                                 formatter_class=RawTextHelpFormatter)
parser.add_argument('fonts', nargs="+")


def main():
  args = parser.parse_args()

  for font_path in args.fonts:
    nametable = nametable_from_filename(font_path)
    font = TTFont(font_path)
    font_filename = ntpath.basename(font_path)

    font['name'] = nametable
    style = font_filename[:-4].split('-')[-1]
    font['OS/2'].usWeightClass = set_usWeightClass(style)
    font['OS/2'].fsSelection = set_fsSelection(font['OS/2'].fsSelection, style)
    win_style = font['name'].getName(2, 3, 1, 1033).string.decode('utf_16_be')
    font['head'].macStyle = set_macStyle(win_style)

    font.save(font_path + '.fix')
    print 'font saved %s.fix' % font_path


if __name__ == '__main__':
  main()
