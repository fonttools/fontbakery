#!/usr/bin/python
# -*- coding: utf-8 -*-

# taken from https://code.google.com/p/googlefontdirectory/source/browse/tools/genmetadata/genmetadata.py
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
# A script for generating METADATA.json files, using fontTools.
#
# Ported to Python 3.x by Mikhail Kashkin
from __future__ import print_function
from __future__ import unicode_literals

from datetime import date
from fontTools import ttLib

import io
import json
import os
import sys
import gzip

if sys.version < '3':
    import codecs
    def u(x):
        if not x:
            return ''
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

# This is only here to have the JSON file data written in a predictable way
# We only care about the the json object being able to iterate over the keys, so
# other stuff might be broken...
METADATA_JSON = 'METADATA.json'
METADATA_JSON_NEW = 'METADATA.json.new'


def check_regular(filename):
    fontdata = fontToolsOpenFont(filename)
    isRegular = True

    if fontdata['OS/2'].fsSelection & 0b10001:
        isRegular = False
    if fontdata['head'].macStyle & 0b11:
        isRegular = False

    return fontdata['OS/2'].usWeightClass == 400 and isRegular

import sys
if sys.version_info[0] < 3:
    def unicode(str):
        return str.decode('utf-8')


def listdir(familydir):
    files = []
    for dirpath, dirnames, filenames in os.walk(familydir):
        files += [os.path.join(dirpath, fn)
                  for fn in filenames if unicode(fn.lower()).endswith('.ttf')]
    return files


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
        self.orderedKeys.remove(key)

    def clear(self):
        dict.clear(self)
        self.orderedKeys = []

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
        return iter(list(self.items()))

    def iterkeys(self):
        return iter(self.orderedKeys)

    # That's definitely a mess, but doing our best
    def update(self, dictionary=None, **kwargs):
        for key in dictionary.keys():
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

    def __getattr__(self, key):
        return dict.get(self, key)

    def popitem(self):
        if self.orderedKeys:
            return self.pop(self.orderedKeys[0])
        return dict.popitem(self)  # should raise KeyError


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
    "vietnamese",
    "devanagari"
])

# DC This should check the NAME table for correct values of the license
# and licenseurl keys


def inferLicense(familydir):
    from bakery_cli.utils import UpstreamDirectory
    directory = UpstreamDirectory(familydir)

    if not directory.LICENSE:
        return ""

    with io.open(directory.LICENSE[0]) as fp:
        content = fp.read()
        if 'Apache License' in content:
            return 'Apache2'
        if 'SIL Open Font License, Version 1.1' in content:
            return 'OFL'
        if 'UBUNTU FONT LICENCE Version 1.0' in content:
            return 'UFL'
    return ""

# DC This should check the italicangle matches the other ways italic can
# be seen - filename, full name, psname, macstyle, others?


def inferStyle(ftfont):
    if ftfont['post'].italicAngle == 0.0:
        return "normal"
    return "italic"

# DC This should check both names match, and match across the family


def inferFamilyName(familydir):
    NAMEID_FAMILYNAME = 1
    NAMEID_STYLE = 2
    files = listdir(familydir)
    familyName = ""
    styleName = ""
    for f in files:
        if check_regular(f):
            ftfont = fontToolsOpenFont(f)
            for record in ftfont['name'].names:
                if record.nameID == NAMEID_FAMILYNAME:
                    if b'\000' in record.string:
                        familyName = record.string.decode('utf-16-be').encode('utf-8')
                    else:
                        familyName = record.string
                # Some authors creates TTF with wrong family name including styles
                if record.nameID == NAMEID_STYLE:
                    if b'\000' in record.string:
                        styleName = record.string.decode('utf-16-be').encode('utf-8')
                    else:
                        styleName = record.string

    familyName = familyName.replace(styleName, '').strip()

    if familyName == "":
        string = "FATAL: No *-Regular.ttf found to set family name!"
        color = "red"
        ansiprint(string, color)
        return "UNKNOWN"
    else:
        return familyName


def fontToolsOpenFont(filepath):
    f = io.open(filepath, 'rb')
    try:
        return ttLib.TTFont(f)
    except:
        print(filepath)
        raise


# DC This should check both copyright strings match
def fontToolsGetCopyright(ftfont):
    # return 'COPYRIGHT'
    NAMEID_PSNAME = 0
    copyright = ""
    for record in ftfont['name'].names:
        if record.nameID == NAMEID_PSNAME and not copyright:
            if b'\000' in record.string:
                try:
                    copyright = u(record.string.decode('utf-16-be'))
                except:
                    copyright = 'COPYRIGHT'
            else:
                copyright = str(record.string)
        if copyright:
            return copyright
        # DC What happens if there is no copyright set?

# DC This should check both names match, and stems match across the family


def fontToolsGetPSName(ftfont):
    NAMEID_PSNAME = 6
    psName = ""
    for record in ftfont['name'].names:
        if record.nameID == NAMEID_PSNAME and not psName:
            if b'\000' in record.string:
                psName = record.string.decode('utf-16-be').encode('utf-8')
            else:
                psName = record.string
        if psName:
            return psName
        # DC What happens if there is no PSName set?

# DC This should check both names match, and stems match across the
# family, and italic/bold match other metadata (weight, macstyle,
# italicangle)


def fontToolsGetFullName(ftfont):
    NAMEID_FULLNAME = 4
    fullName = ""
    for record in ftfont['name'].names:
        if record.nameID == NAMEID_FULLNAME and not fullName:
            if b'\000' in record.string:
                fullName = record.string.decode('utf-16-be').encode('utf-8')
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
            if b'\000' in record.string:
                desName = record.string.decode('utf-16-be').encode('utf-8')
            else:
                desName = record.string
        if desName:
            return desName

# DC This should check both names match


def fontToolsGetDesc(ftfont):
    NAMEID_DESC = 10
    fontDesc = False
    for record in ftfont['name'].names:
        if record.nameID == NAMEID_DESC and not fontDesc:
            if b'\000' in record.string:
                fontDesc = record.string.decode('utf-16-be').encode('utf-8')
            else:
                fontDesc = record.string
            break
    if not fontDesc:
        fontDesc = "TODO"
    return fontDesc

# DC NameIDs are as follows:
# required marked *
#    0  Copyright notice.
#  * 1  Family name
#  * 2  Font Subfamily name (should matcht the OS/2.fsSelection bit - eg, fsSelection bit 6 set = Regular)
#  * 4  Full name
#    5  Version string (Should be 'Version <number>.<number>' Caps with a space between “Version” and the number; one or more digits (0-9) of value less than 65535 followed by period followed by one or more digits of value less than 65535; Any character other than a digit will terminate the minor number and act as comment string “;” is sometimes used)
#  * 6  Postscript name (Must have Platform: 1 [Macintosh]; Platform-specific encoding: 0 [Roman]; Language: 0 [English]  and Platform: 3 [Windows]; Platform-specific encoding: 1 [Unicode]; Language: 0x409 [English (American)]  and any nameID=6s other than those are out of spec; both must be identical; no longer than 63 characters; and restricted to the printable ASCII subset, codes 33 through 126; identical to the font name as stored in the CFF's Name INDEX;
#    7  Trademark
#    8  Manufacturer Name.
#    9  Designer Name
#    10 Description
#    11 URL Vendor (should have http://)
#    12 URL Designer (should have http://)
#    13 License Description
#    14 License URL
#    16 Preferred Family; must be different to ID 1 but make sense
#    17 Preferred Subfamily; must be different to ID 2, and unique in the Prefered Family
#    18 Compatible Full (Macintosh only); matches the Full Name
#    19 Sample text (best sample to display the font in)

# DC This should use fontTools not FontForge for everything


def createFonts(familydir, familyname):
    from operator import attrgetter
    fonts = []
    files = listdir(familydir)
    for f in files:
        fontmetadata = InsertOrderedDict()
        ftfont = fontToolsOpenFont(f)
        fontmetadata["name"] = u(familyname)
        fontmetadata["postScriptName"] = u(fontToolsGetPSName(ftfont))
        fontmetadata["fullName"] = u(fontToolsGetFullName(ftfont))
        fontmetadata["style"] = u(inferStyle(ftfont))
        fontmetadata["weight"] = ftfont['OS/2'].usWeightClass
        fontmetadata["filename"] = os.path.basename(unicode(f).lstrip('./'))
        fontmetadata["copyright"] = u(fontToolsGetCopyright(ftfont))
        fonts.append(fontmetadata)
    return sorted(fonts, key=attrgetter('weight'))

# DC This should also print the subset filesizes and check they are
# smaller than the original ttf


def inferSubsets(familydir):
    subsets = set()
    files = listdir(familydir)
    for f in files:
        index = unicode(f).rfind(".")
        if index != -1:
            extension = unicode(f)[index + 1:]
            if extension in SUPPORTED_SUBSETS:
                subsets.add(extension)
    if len(subsets) == 0:
        return ["latin"]
    return sorted(subsets)


def getDesigner(familydir):
    # import fontforge
    files = listdir(familydir)
    for f in files:
        if check_regular(f):  # DC should ansiprint red if no Reg exemplar
            ftfont = fontToolsOpenFont(f)
            desName = fontToolsGetDesignerName(ftfont)
            if isinstance(desName, str):
                string = u"Designer's name from font is: " + u(desName)
                color = "green"
                ansiprint(string, color)
                return u(desName)
            else:
                desName = "Multiple Designers"
                ansiprint(
                    "No Designer Name known, using Multiple Designers for now...", "red")
                return desName


def check_monospace(familydir):
    files = listdir(familydir)
    glyphwidths = []
    for f in files:
        if not unicode(f).endswith('.ttf'):
            continue
        font = fontToolsOpenFont(unicode(f))
        for table in font['cmap'].tables:
            if not (table.platformID == 3 and table.platEncID in [1, 10]):
                continue

            for glyphname in table.cmap:
                try:
                    glyphwidths.append(font['hmtx'][glyphname][0])
                except (IndexError, KeyError):
                    # can't read hmtx for glyphname, append value of zero
                    glyphwidths.append(0)
    # if all glyphs has the same widths then it is easy to check
    # by casting list to python sets.
    return len(set(glyphwidths)) == 1


def getSize(familydir):
    files = listdir(familydir)
    matchedFiles = []
    for f in files:
        if check_regular(f):
            matchedFiles.append(f)
    if matchedFiles == []:
        gzipSize = str(-1)
        string = "WARNING: No *-Regular.ttf to calculate gzipped filesize!"
        color = "red"
    else:
        filepath = matchedFiles[0]
        tmpgzip = "/tmp/tempfont.gz"
        string = "Original size: "
        string += str(os.path.getsize(filepath))
        f_in = io.open(filepath, 'rb')
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
        print(metadata)
    familyname = inferFamilyName(familydir)

    if not metadata.get('name') or metadata.get('name', "UNKNOWN") == "UNKNOWN":
        metadata["name"] = familyname

    desName = getDesigner(familydir)
    if not metadata.get('designer'):
        metadata["designer"] = desName
                    # DC Should check it against profiles.json

    if not metadata.get('license'):
        metadata["license"] = inferLicense(familydir)

    setIfNotPresent(metadata, "visibility", "Sandbox")

    category = ''
    if check_monospace(familydir):
        category = 'monospace'
    setIfNotPresent(metadata, "category", category)
                    # DC Should get this from the font or prompt?

    if not metadata.get('size') or metadata.get('size', -1) == -1:
        metadata["size"] = getSize(familydir)
                    # DC: this should check the filesize got smaller than last
                    # time
    metadata["fonts"] = createFonts(familydir, familyname)
    metadata["subsets"] = inferSubsets(familydir)
    setIfNotPresent(metadata, "dateAdded", getToday())
                    # DC This is used for the Date Added sort in the GWF
                    # Directory - DC to check all existing values in hg repo
                    # are correct
    return metadata


def getToday():
    return str(date.today().strftime("%Y-%m-%d"))


def hasMetadata(familydir):
    fn = os.path.join(familydir, METADATA_JSON)
    return os.path.exists(fn) and (os.path.getsize(fn) > 0)


def loadMetadata(familydir):
    import collections
    with io.open(os.path.join(familydir, METADATA_JSON), 'r', encoding="utf-8") as fp:
        return json.load(fp, object_pairs_hook=collections.OrderedDict)


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
        newlines.append(u"%s\n" % (line.rstrip()))
    return u"".join(newlines)


def writeFile(familydir, metadata):
    filename = METADATA_JSON
    if hasMetadata(familydir):
        filename = METADATA_JSON_NEW

    with io.open(os.path.join(familydir, filename), 'w', encoding='utf-8') as f:
        contents = json.dumps(metadata, indent=2, ensure_ascii=False)
        f.write(striplines(contents))

    print(json.dumps(metadata, indent=2, ensure_ascii=False))


def ansiprint(string, color):
    if sys.stdout.isatty():
        attr = []
        if color == "green":
            attr.append('32')  # green
            attr.append('1')  # bold
        else:
            attr.append('31')  # red
            attr.append('1')  # bold
        print('\x1b[%sm%s\x1b[0m' % (';'.join(attr), string))
    else:
        print(string)


def writeDescHtml(familydir):
    filename = "DESCRIPTION.en_us.html"
    if os.path.exists(os.path.join(familydir, filename)):
        ansiprint('{} exists', 'green')
        return

    foundRegular = False
    files = listdir(familydir)
    for f in files:
        if check_regular(f):
            foundRegular = True
            filepath = os.path.join(familydir, f)
            ftfont = fontToolsOpenFont(filepath)
            fontDesc = fontToolsGetDesc(ftfont)
            break

    if not foundRegular:
        string = "No Regular found! REMEMBER! Create a " + filename
        color = "red"
        ansiprint(string, color)
        fontDesc = "TODO"

    descHtml = u"<p>" + u(fontDesc) + u"</p>"
    with io.open(os.path.join(familydir, filename), 'w', encoding="utf-8") as f:
        f.write(descHtml)


def run(familydir):
    writeDescHtml(familydir)
    writeFile(familydir, genmetadata(familydir))
