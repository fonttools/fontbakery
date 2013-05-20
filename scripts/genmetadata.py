#!/usr/bin/python
# -*- coding: utf-8 -*-

# taken from https://code.google.com/p/googlefontdirectory/source/browse/tools/genmetadata/genmetadata.py

import sys
sys.path.append('/usr/local/lib/python2.7/site-packages/')

#
# Copyright 2012, Google Inc.
# Author: Jeremie Lenfant-Engelmann (jeremiele a google com)
# Author: Dave Crossland (dcrossland a google com )
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Portions Copyright (c) 2003, Michael C. Fletcher, TTFQuery Project
#
# A script for generating METADATA.json files, using fontTools,
# written in Python 2.6

from datetime import date
from fontTools import ttLib

import codecs
import json
import logging
import os
import sys
import gzip

# This is only here to have the JSON file data written in a predictable way
# We only care about the the json object being able to iterate over the keys, so
# other stuff might be broken...
class InsertOrderedDict(dict):

  def __init__(self):
    dict.__init__(self)
    self.orderedKeys = []

  def __setitem__(self, key, item):
    dict.__setitem__(self, key, item)
    if key not in self.orderedKeys:
      self.orderedKeys.append(key)

  def __delitem__(self, key):
    dict.__delitem__(self, key)
    orderedKeys.remove(key)

  def clear(self):
    dict.clear(self)
    orderedKeys = []

  def copy(self):
    dictCopy = InsertOrderedDict()
    for key in self.orderedKeys:
      dictCopy[key] = dict.get(self, key)
    return dictCopy

  def keys(self):
    return self.orderedKeys

  def items(self):
    return [(key, dict.get(self, key)) for key in self.orderedKeys]

  def iteritems(self):
    return iter(self.items())

  def iterkeys(self):
    return iter(self.orderedKeys)

  # That's definitely a mess, but doing our best
  def update(self, dictionary=None, **kwargs):
    for key in dictionary.iterkeys():
      if key not in self.orderedKeys:
        self.orderedKeys.append(key)
    if len(kwargs):
      for key in kwargs:
        if key not in self.orderedKeys:
          self.orderedKeys.append(key)
    dict.update(self, dictionary, **kwargs)

  def pop(self, key, *args):
    self.orderedKeys.remove(key)
    return dict.pop(self, key, *args)

  def popitem(self):
    if self.orderedKeys:
      return self.pop(self.orderedKeys[0])
    return dict.popitem(self) # should raise KeyError

SUPPORTED_SUBSETS = frozenset([
    "menu",
    "arabic",
    "armenian",
    "balinese",
    "bengali",
    "burmese",
    "cherokee",
    "cyrillic",
    "cyrillic-ext",
    "ethiopic",
    "georgian",
    "greek",
    "greek-ext",
    "gujarati",
    "hebrew",
    "hindi",
    "japanese",
    "javanese",
    "kannada",
    "khmer",
    "korean",
    "lao",
    "latin",
    "latin-ext",
    "malayalam",
    "oriya",
    "osmanya",
    "sinhala",
    "tamil",
    "telugu",
    "thai",
    "tibetan",
    "vietnamese"
])

def usage():
  print >> sys.stderr, "genmetadata.py family_directory"

# DC This should check the NAME table for correct values of the license and licenseurl keys
def inferLicense(familydir):
  if familydir.find("ufl/") != -1:
    return "UFL"
  if familydir.find("ofl/") != -1:
    return "OFL"
  if familydir.find("apache/") != -1:
    return "Apache2"
  return ""

# DC This should check the italicangle matches the other ways italic can be seen - filename, full name, psname, macstyle, others?
def inferStyle(ftfont):
  if ftfont['post'].italicAngle == 0.0:
    return "normal"
  return "italic"

# DC This should check both names match, and match across the family
def inferFamilyName(familydir):
  NAMEID_FAMILYNAME = 1
  files = os.listdir(familydir)
  familyName = ""
  for f in files:
    if f.endswith("Regular.ttf"):
      filepath = os.path.join(familydir, f)
      ftfont = fontToolsOpenFont(filepath)
      for record in ftfont['name'].names:
        if record.nameID == NAMEID_FAMILYNAME:
          if '\000' in record.string:
            familyName = unicode(record.string, 'utf-16-be').encode('utf-8')
          else:
            familyName = record.string
  if familyName == "":
    string = "FATAL: No *-Regular.ttf found to set family name!"
    color = "red"
    ansiprint(string, color)
    sys.exit()
  else:
    return familyName

def fontToolsOpenFont(filepath):
  if isinstance(filepath, (str,unicode)):
    file = open(filepath, 'rb')
    return ttLib.TTFont(file)


# DC This should check both copyright strings match
def fontToolsGetCopyright(ftfont):
#  return 'COPYRIGHT'
  NAMEID_PSNAME = 0
  copyright = ""
  for record in ftfont['name'].names:
    if record.nameID == NAMEID_PSNAME and not copyright:
      if '\000' in record.string:
        copyright = unicode(record.string, 'utf-16-be').encode('utf-8')
      else:
        copyright = record.string
    if copyright:
      return copyright
    # DC What happens if there is no copyright set?

# DC This should check both names match, and stems match across the family
def fontToolsGetPSName(ftfont):
  NAMEID_PSNAME = 6
  psName = ""
  for record in ftfont['name'].names:
    if record.nameID == NAMEID_PSNAME and not psName:
      if '\000' in record.string:
        psName = unicode(record.string, 'utf-16-be').encode('utf-8')
      else:
        psName = record.string
    if psName:
      return psName
    # DC What happens if there is no PSName set?

# DC This should check both names match, and stems match across the family, and italic/bold match other metadata (weight, macstyle, italicangle)
def fontToolsGetFullName(ftfont):
  NAMEID_FULLNAME = 4
  fullName = ""
  for record in ftfont['name'].names:
    if record.nameID == NAMEID_FULLNAME and not fullName:
      if '\000' in record.string:
        fullName = unicode(record.string, 'utf-16-be').encode('utf-8')
      else:
        fullName = record.string
    if fullName:
      return fullName

# DC This should check both names match, and is found in designers.json
def fontToolsGetDesignerName(ftfont):
#  return 'DESIGNER'
  NAMEID_DESIGNERNAME = 9
  desName = ""
  for record in ftfont['name'].names:
    if record.nameID == NAMEID_DESIGNERNAME and not desName:
      if '\000' in record.string:
        desName = unicode(record.string, 'utf-16-be').encode('utf-8')
      else:
        desName = record.string
    if desName:
      return desName

# DC This should check both names match
def fontToolsGetDesc(ftfont):
  NAMEID_DESC = 10
  fontDesc = ""
  for record in ftfont['name'].names:
    if record.nameID == NAMEID_DESC and not fontDesc:
      if '\000' in record.string:
        fontDesc = unicode(record.string, 'utf-16-be').encode('utf-8')
      else:
        fontDesc = record.string
    if fontDesc:
      return fontDesc

# DC NameIDs are as follows:
#    0	Copyright notice.
#    1	Family name
#    2	Font Subfamily name (should matcht the OS/2.fsSelection bit - eg, fsSelection bit 6 set = Regular)
#    5	Version string (Should be 'Version <number>.<number>' Caps with a space between “Version” and the number; one or more digits (0-9) of value less than 65535 followed by period followed by one or more digits of value less than 65535; Any character other than a digit will terminate the minor number and act as comment string “;” is sometimes used)
#    6	Postscript name (Must have Platform: 1 [Macintosh]; Platform-specific encoding: 0 [Roman]; Language: 0 [English]  and Platform: 3 [Windows]; Platform-specific encoding: 1 [Unicode]; Language: 0x409 [English (American)]  and any nameID=6s other than those are out of spec; both must be identical; no longer than 63 characters; and restricted to the printable ASCII subset, codes 33 through 126; identical to the font name as stored in the CFF's Name INDEX;
#    7	Trademark
#    8	Manufacturer Name.
#    9	Designer Name
#    10	Description
#    11	URL Vendor (should have http://)
#    12	URL Designer (should have http://)
#    13	License Description
#    14	License URL
#    16	Preferred Family; must be different to ID 1 but make sense
#    17	Preferred Subfamily; must be different to ID 2, and unique in the Prefered Family
#    18	Compatible Full (Macintosh only); matches the Full Name
#    19	Sample text (best sample to display the font in)

# DC This should use fontTools not FontForge for everything
def createFonts(familydir, familyname):
  fonts = []
  files = os.listdir(familydir)
  for f in files:
    if f.endswith(".ttf"):
      fontmetadata = InsertOrderedDict()
      filepath = os.path.join(familydir, f)
      ftfont = fontToolsOpenFont(filepath)
      fontmetadata["name"] = familyname
      ansiprint("Family Name: " + fontmetadata["name"], "green")
      fontmetadata["postScriptName"] = fontToolsGetPSName(ftfont)
      ansiprint("PS Name: " + fontmetadata["postScriptName"], "green")
      fontmetadata["fullName"] = fontToolsGetFullName(ftfont)
      ansiprint("Full Name: " + fontmetadata["fullName"], "green")
      fontmetadata["style"] = inferStyle(ftfont)
      ansiprint("Style: " + fontmetadata["style"], "green")
      fontmetadata["weight"] = ftfont['OS/2'].usWeightClass
      ansiprint("Weight: " + str(fontmetadata["weight"]), "green")
      fontmetadata["filename"] = f
      ansiprint("Filename: " + fontmetadata["filename"], "green")
      fontmetadata["copyright"] = fontToolsGetCopyright(ftfont)
      ansiprint("Copyright: " + fontmetadata["copyright"], "green")
      fonts.append(fontmetadata)
  return fonts

# DC This should also print the subset filesizes and check they are smaller than the original ttf
def inferSubsets(familydir):
  subsets = set()
  files = os.listdir(familydir)
  for f in files:
    index = f.rfind(".")
    if index != -1:
      extension = f[index + 1:]
      if extension in SUPPORTED_SUBSETS:
        subsets.add(extension)
  if len(subsets) == 0:
    return ["latin"]
  return sorted(subsets)

def getDesigner(familydir):
    files = os.listdir(familydir)
    for f in files:
        if f.endswith("Regular.ttf"): #DC should ansiprint red if no Reg exemplar
          filepath = os.path.join(familydir, f)
          ftfont = fontToolsOpenFont(filepath)
          desName = fontToolsGetDesignerName(ftfont)
          if isinstance(desName, (str,unicode)):
            string = "Designer's name from font is: " + desName
            color = "green"
            ansiprint(string, color)
            return desName
          else:
            desName = unicode(raw_input("Designer?\n"))
            if desName == "":
              desName = "Multiple Designers"
              ansiprint("No Designer Name known, using Multiple Designers for now...", "red")
              return desName
            else:
              string = "Designer's name from input is " + desName
              color = "green"
              ansiprint(string, color)
              return desName

def getSize(familydir):
    files = os.listdir(familydir)
    matchedFiles = []
    for f in files:
      if f.endswith("Regular.ttf"):
        matchedFiles.append(f)
    if matchedFiles == []:
      gzipSize = str(-1)
      string = "WARNING: No *-Regular.ttf to calculate gzipped filesize!"
      color = "red"
    else:
      filepath = os.path.join(familydir, matchedFiles[0])
      tmpgzip = "/tmp/tempfont.gz"
      string = "Original size: "
      string += str(os.path.getsize(filepath))
      f_in = open(filepath, 'rb')
      f_out = gzip.open(tmpgzip, 'wb')
      f_out.writelines(f_in)
      f_out.close()
      f_in.close()
      gzipSize = str(os.path.getsize(tmpgzip))
      string += "\nGzip size: "
      string += gzipSize
      color = "green"
    ansiprint(string, color)
    return int(gzipSize)

def setIfNotPresent(metadata, key, value):
  if key not in metadata:
    metadata[key] = value

def genmetadata(familydir):
  metadata = InsertOrderedDict()
  if hasMetadata(familydir):
    metadata = loadMetadata(familydir)
  familyname = inferFamilyName(familydir)
  setIfNotPresent(metadata, "name", familyname)
  setIfNotPresent(metadata, "designer", getDesigner(familydir))  # DC Should check it against profiles.json
  setIfNotPresent(metadata, "license", inferLicense(familydir))
  setIfNotPresent(metadata, "visibility", "Sandbox")
  setIfNotPresent(metadata, "category", "") # DC Should get this from the font or prompt?
  setIfNotPresent(metadata, "size", getSize(familydir)) # DC: this should check the filesize got smaller than last time
  setIfNotPresent(metadata, "dateAdded", getToday())  # DC This is used for the Date Added sort in the GWF Directory - DC to check all existing values in hg repo are correct
  metadata["fonts"] = createFonts(familydir, familyname)
  metadata["subsets"] = inferSubsets(familydir)
  return metadata

def getToday():
  return unicode(date.today().strftime("%Y-%m-%d"))

def hasMetadata(familydir):
  return os.path.exists(os.path.join(familydir, "METADATA.json"))

def loadMetadata(familydir):
  with codecs.open(os.path.join(familydir, "METADATA.json"), 'r', encoding="utf_8") as fp:
    return sortOldMetadata(json.load(fp))

def sortOldMetadata(oldmetadata):
  orderedMetadata = InsertOrderedDict()
  orderedMetadata["name"] = oldmetadata["name"]
  orderedMetadata["designer"] = oldmetadata["designer"]
  orderedMetadata["license"] = oldmetadata["license"]
  orderedMetadata["visibility"] = oldmetadata["visibility"]
  orderedMetadata["category"] = oldmetadata["category"]
  orderedMetadata["size"] = oldmetadata["size"]
  orderedMetadata["fonts"] = sortFont(oldmetadata["fonts"])
  orderedMetadata["subsets"] = sorted(oldmetadata["subsets"])
  orderedMetadata["dateAdded"] = oldmetadata["dateAdded"]
  return orderedMetadata

def sortFont(fonts):
  sortedfonts = []
  for font in fonts:
    fontMetadata = InsertOrderedDict()
    fontMetadata["name"] = font["name"]
    fontMetadata["style"] = font["style"]
    fontMetadata["weight"] = font["weight"]
    fontMetadata["filename"] = font["filename"]
    fontMetadata["postScriptName"] = font["postScriptName"]
    fontMetadata["fullName"] = font["fullName"]
    fontMetadata["copyright"] = font["copyright"]
    sortedfonts.append(fontMetadata)
  return sortedfonts

def striplines(jsontext):
  lines = jsontext.split("\n")
  newlines = []
  for line in lines:
    newlines.append("%s\n" % (line.rstrip()))
  return "".join(newlines)

def writeFile(familydir, metadata):
  filename = "METADATA.json"
  if hasMetadata(familydir):
    filename = "METADATA.json.new"
  with codecs.open(os.path.join(familydir, filename), 'w', encoding="utf_8") as f:
    f.write(striplines(json.dumps(metadata, indent=2, ensure_ascii=True)))
  print json.dumps(metadata, indent=2, ensure_ascii=True)

def ansiprint(string, color):
  if sys.stdout.isatty():
    attr = []
    if color == "green":
        attr.append('32') # green
        attr.append('1') # bold
    else:
        attr.append('31') # red
        attr.append('1') # bold
    print '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
  else:
    print string

def writeDescHtml(familydir):
  filename = "DESCRIPTION.en_us.html"
  fullPath = os.path.join(familydir, filename)
  if os.path.exists(fullPath):
    string = filename + " exists - check it is okay: "
    color = "green"
    ansiprint(string, color)
    f = open(fullPath)
    print f.read()
    return
  else:
    # DC sanitize this raw_input as real HTML
    files = os.listdir(familydir)
    for f in files:
      if f.endswith("Regular.ttf"):
        filepath = os.path.join(familydir, f)
        ftfont = fontToolsOpenFont(filepath)
        fontDesc = fontToolsGetDesc(ftfont)
      else:
        string = "No Regular found, only " + f
        color = "red"
        ansiprint(string, color)
    if isinstance(fontDesc, (str,unicode)):
      descHtml = "<p>" + fontDesc + "</p>"
    else:
      descHtml = unicode(raw_input("Description HTML?\n"))
    if descHtml == "":
      string = "REMEMBER! Create a " + filename
      color = "red"
      ansiprint(string, color)
      return
    with codecs.open(os.path.join(familydir, filename), 'w', encoding="utf_8") as f:
      f.write(descHtml)
    string = "Created " + filename + " with:"
    color = "green"
    ansiprint(string, color)
    ansiprint(descHtml, color)

def run(familydir):
 writeDescHtml(familydir)
 writeFile(familydir, genmetadata(familydir))

def main(argv=None):
  if argv is None:
    argv = sys.argv
  if len(argv) != 2:
    usage()
    return 1
  run(argv[1])
  return 0

if __name__ == '__main__':
  sys.exit(main())
