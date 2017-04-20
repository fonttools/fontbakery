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

Replace a collection of fonts nametable's with a new table based on the Google
Fonts naming spec, from just the filename.
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
  "Medium": 500,
  "SemiBold": 600,
  "Bold": 700,
  "ExtraBold": 800,
  "Black": 900
}

FSSELECTION = {
  'Regular': 64,
  'Italic': 1,
  'Bold': 32,
  'Bold Italic': 33,
  'UseTypoMetrics': 128
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

FIELD_ENCODINGS = {
  1: 'mac_roman',
  3: 'utf_16_be'
}

class NameTableFromFilename(object):
  """Convert filename into relevant font name table fields"""
  def __init__(self, filename, font_ver, vendor_id, use_typo_metrics=False):
    self.filename = filename[:-4]
    self.family_name, self.style_name = self.filename.split('-')
    self.family_name = self._split_camelcase(self.family_name)
    self.use_typo_metrics = use_typo_metrics
    self.font_version = font_ver
    self.vendor_id = vendor_id

  @property
  def mac_family_name(self):
    return self.family_name

  @property
  def win_family_name(self):
    name = self.family_name
    if self.style_name not in WIN_SAFE_STYLES:
      name = '%s %s' % (self.family_name, self.style_name)
    if 'Italic' in name:
      name = re.sub(r'Italic', r'', name)
    return name

  @property
  def mac_subfamily_name(self):
    name = self.style_name
    if name.startswith('Italic'):
      name = name
    elif 'Italic' in name:
      name = name.replace('Italic', ' Italic')
    return name

  @property
  def win_subfamily_name(self):
    name = self.style_name
    if 'BoldItalic' == name:
      return 'Bold Italic'
    elif 'Italic' in name:
      return 'Italic'
    elif name == 'Bold':
      return 'Bold'
    else:
      return 'Regular'

  @property
  def unique_id(self):
    # Glyphsapp style 2.000;MYFO;Arsenal-Bold
    # version;vendorID;filename
    return '%s;%s;%s' % (self.version, self.vendor_id, self.filename)

  @property
  def full_name(self):
    name = '%s %s' % (self.family_name, self.style_name)
    if self.style_name.startswith('Italic'):
      name = name
    elif 'Italic' in self.style_name:
      name = name.replace('Italic', ' Italic')
    return name

  @property
  def postscript_name(self):
    return self.filename

  @property
  def pref_family_name(self):
    return self.mac_family_name

  @property
  def pref_subfamily_name(self):
    return self.mac_subfamily_name

  @property
  def usWeightClass(self):
    name = self.style_name
    if 'Italic' == self.style_name:
      name = 'Regular'
    elif 'Italic' in self.style_name:
      name = re.sub(r'Italic', r'', name)
    return WEIGHTS[name]

  @property
  def macStyle(self):
    return MACSTYLE[self.win_subfamily_name]

  @property
  def fsSelection(self):
    if self.use_typo_metrics:
      f = FSSELECTION['UseTypoMetrics']
      return FSSELECTION[self.win_subfamily_name] + f
    return FSSELECTION[self.win_subfamily_name]

  @property
  def version(self):
    return re.search(r'[0-9]{1,4}\.[0-9]{1,8}', self.font_version).group(0)

  def _split_camelcase(self, text):
    return re.sub(r"(?<=\w)([A-Z])", r" \1", text)

  def __dict__(self):
    # Mapping for fontTools getName method in the name table
    # nameID, platformID, platEncID, langID
    d = {
      # Mac
      (1, 1, 0, 0): self.mac_family_name,
      (2, 1, 0, 0): self.mac_subfamily_name,
      (3, 1, 0, 0): self.unique_id,
      (4, 1, 0, 0): self.full_name,
      (6, 1, 0, 0): self.postscript_name,
      (16, 1, 0, 0): self.pref_family_name,
      (17, 1, 0, 0): self.pref_subfamily_name,
      # Win
      (1, 3, 1, 1033): self.win_family_name,
      (2, 3, 1, 1033): self.win_subfamily_name,
      (3, 3, 1, 1033): self.unique_id,
      (4, 3, 1, 1033): self.full_name,
      (6, 3, 1, 1033): self.postscript_name,
      (16, 3, 1, 1033): self.pref_family_name,
      (17, 3, 1, 1033): self.pref_subfamily_name
    }
    return d

  def __getitem__(self, key):
    return self.__dict__()[key]

  def __iter__(self):
    for i in self.__dict__():
      yield i


parser = argparse.ArgumentParser(description=description,
                 formatter_class=RawTextHelpFormatter)
parser.add_argument('fonts', nargs="+")


def typo_metrics_enabled(fsSelection):
  fsSelection_on = fsSelection & 0b10000000
  if fsSelection_on:
    return True
  return False


def main():
  args = parser.parse_args()

  for font_path in args.fonts:
    font_filename = ntpath.basename(font_path)
    font = TTFont(font_path)
    font_vendor = font['OS/2'].achVendID
    font_version = font['name'].getName(5, 3, 1, 1033)
    font_version = str(font_version).decode(font_version.getEncoding())
    typo_enabled = typo_metrics_enabled(font['OS/2'].fsSelection)
    new_names = NameTableFromFilename(font_filename,
                                      font_version,
                                      font_vendor,
                                      typo_enabled)

    new_nametable = newTable('name')
    for field in REQUIRED_FIELDS:
      string = None
      if field in new_names:
        string = new_names[field]
      elif font['name'].getName(*field):
        string = str(font['name'].getName(*field).string).decode(FIELD_ENCODINGS[field[1]])
      elif font['name'].getName(field[0], 3, 1, 1033): # use windows field
        string = str(font['name'].getName(field[0], 3, 1, 1033).string).decode(FIELD_ENCODINGS[3])
      elif font['name'].getName(field[0], 1, 0, 0): # use mac field
        string = str(font['name'].getName(field[0], 1, 0, 0).string).decode(FIELD_ENCODINGS[1])

      if string:
        new_nametable.setName(string.encode(FIELD_ENCODINGS[field[1]]), *field)

    font['name'] = new_nametable
    font['OS/2'].usWeightClass = new_names.usWeightClass
    font['OS/2'].fsSelection = new_names.fsSelection
    font['head'].macStyle = new_names.macStyle

    font.save(font_path + '.fix')
    print 'font saved %s.fix' % font_path


if __name__ == '__main__':
  main()
