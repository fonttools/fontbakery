#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import json

"""This creates a list of open type name table entries, suitable for
setting to a font with `ot_tables_tool.setNames`

One entry is in the form:
    [
        (string)data
      , (int)nameID
      , (int)platformID
      , (int)platEncID
      , (hex-string)langID
    ]


The table entries are shaped according to the google fonts "OpenType Naming Help Sheet"
https://docs.google.com/spreadsheets/d/1ckHigO7kRxbm9ZGVQwJ6QJG_HjV_l_IRWJ_xeWnTSBg/edit#gid=0
"""

# name table info: https://www.microsoft.com/typography/otspec/name.htm
WIN_ID = 3
MAC_ID = 1

PLAT_ENC_IDS = {
    WIN_ID: 1 # Unicode BMP (UCS-2)
  , MAC_ID: 0 # Roman
}

WIN_LANG_ID_2_MAC_LANG_ID = {
    '0x409': 0 # 0 English
}

WEIGHT_NAME_2_WEIGHT_CLASS = {
    'Thin': 250
  , 'ExtraLight': 275
  , 'Light': 300
  , 'Regular': 400
  , 'Medium': 500
  , 'SemiBold': 600
  , 'Bold': 700
  , 'ExtraBold': 800
  , 'Black': 900
}

NAME_IDS = {
     'copyright': 0  # Copyright notice.
    ,'fontFamilyName': 1  # Font Family name. Up to four fonts can share the Font Family name, forming a font style linking group (regular, italic, bold, bold italic — as defined by OS/2.fsSelection bit settings).
    ,'fontSubfamilyName': 2  # Font Subfamily name. The Font Subfamily name distiguishes the font in a group with the same Font Family name (name ID 1). This is assumed to address style (italic, oblique) and weight (light, bold, black, etc.). A font with no particular differences in weight or style (e.g. medium weight, not italic and fsSelection bit 6 set) should have the string “Regular” stored in this position.
    ,'fontIdentifier': 3  # Unique font identifier
    ,'fullFontName': 4  # Full font name; a combination of strings 1 and 2, or a similar human-readable variant. If string 2 is "Regular", it is sometimes omitted from name ID 4.
    ,'version': 5  # Version string. Should begin with the syntax 'Version <number>.<number>' (upper case, lower case, or mixed, with a space between “Version” and the number).
            # The string must contain a version number of the following form: one or more digits (0-9) of value less than 65,535, followed by a period, followed by one or more digits of value less than 65,535. Any character other than a digit will terminate the minor number. A character such as “;” is helpful to separate different pieces of version information.
            # The first such match in the string can be used by installation software to compare font versions. Note that some installers may require the string to start with “Version ”, followed by a version number as above.
    ,'postscriptName': 6  # Postscript name for the font; Name ID 6 specifies a string which is used to invoke a PostScript language font that corresponds to this OpenType font. When translated to ASCII, the name string must be no longer than 63 characters and restricted to the printable ASCII subset, codes 33 – 126, except for the 10 characters '[', ']', '(', ')', '{', '}', '<', '>', '/', '%'.
            # In a CFF OpenType font, there is no requirement that this name be the same as the font name in the CFF’s Name INDEX. Thus, the same CFF may be shared among multiple font components in a Font Collection. See the 'name' table section of Recommendations for OpenType fonts "" for additional information.
    ,'trademark': 7  # Trademark; this is used to save any trademark notice/information for this font. Such information should be based on legal advice. This is distinctly separate from the copyright.
    ,'manufacturer': 8  # Manufacturer Name.
    ,'designer': 9  # Designer; name of the designer of the typeface.
    ,'description': 10 # Description; description of the typeface. Can contain revision information, usage recommendations, history, features, etc.
    ,'urlVendor': 11 # URL Vendor; URL of font vendor (with protocol, e.g., http://, ftp://). If a unique serial number is embedded in the URL, it can be used to register the font.
    ,'urlDesigner': 12 # URL Designer; URL of typeface designer (with protocol, e.g., http://, ftp://).
    ,'licenseDescription': 13 # License Description; description of how the font may be legally used, or different example scenarios for licensed use. This field should be written in plain language, not legalese.
    ,'urlLicense': 14 # License Info URL; URL where additional licensing information can be found.
    ,'_reserved_15': 15 # Reserved.
    ,'typographicFamily': 16 # Typographic Family name: The typographic family grouping doesn't impose any constraints on the number of faces within it, in contrast with the 4-style family grouping (ID 1), which is present both for historical reasons and to express style linking groups. If name ID 16 is absent, then name ID 1 is considered to be the typographic family name. (In earlier versions of the specification, name ID 16 was known as "Preferred Family".)
    ,'typographicSubfamily': 17 # Typographic Subfamily name: This allows font designers to specify a subfamily name within the typographic family grouping. This string must be unique within a particular typographic family. If it is absent, then name ID 2 is considered to be the typographic subfamily name. (In earlier versions of the specification, name ID 17 was known as "Preferred Subfamily".)
    ,'compatibleFull': 18 # Compatible Full (Macintosh only); On the Macintosh, the menu name is constructed using the FOND resource. This usually matches the Full Name. If you want the name of the font to appear differently than the Full Name, you can insert the Compatible Full Name in ID 18.
    ,'sampleText': 19 # Sample text; This can be the font name, or any other text that the designer thinks is the best sample to display the font in.
    ,'postScriptCID ': 20 # PostScript CID findfont name; Its presence in a font means that the nameID 6 holds a PostScript font name that is meant to be used with the “composefont” invocation in order to invoke the font in a PostScript interpreter. See the definition of name ID 6.

            # The value held in the name ID 20 string is interpreted as a PostScript font name that is meant to be used with the “findfont” invocation, in order to invoke the font in a PostScript interpreter.
            # When translated to ASCII, this name string must be restricted to the printable ASCII subset, codes 33 through 126, except for the 10 characters: '[', ']', '(', ')', '{', '}', '<', '>', '/', '%'.

            # See "Recommendations for OTF fonts" for additional information
    ,'wwsFamilyName': 21 # WWS Family Name. Used to provide a WWS-conformant family name in case the entries for IDs 16 and 17 do not conform to the WWS model. (That is, in case the entry for ID 17 includes qualifiers for some attribute other than weight, width or slope.) If bit 8 of the fsSelection field is set, a WWS Family Name entry should not be needed and should not be included. Conversely, if an entry for this ID is include, bit 8 should not be set. (See OS/2 'fsSelection' field for details.) Examples of name ID 21: “Minion Pro Caption” and “Minion Pro Display”. (Name ID 16 would be “Minion Pro” for these examples.)
    ,'wwsSubfamilyName': 22 # WWS Subfamily Name. Used in conjunction with ID 21, this ID provides a WWS-conformant subfamily name (reflecting only weight, width and slope attributes) in case the entries for IDs 16 and 17 do not conform to the WWS model. As in the case of ID 21, use of this ID should correlate inversely with bit 8 of the fsSelection field being set. Examples of name ID 22: “Semibold Italic”, “Bold Condensed”. (Name ID 17 could be “Semibold Italic Caption”, or “Bold Condensed Display”, for example.)
    ,'lightBackgoundPalette': 23 # Light Backgound Palette. This ID, if used in the CPAL table’s Palette Labels Array, specifies that the corresponding color palette in the CPAL table is appropriate to use with the font when displaying it on a light background such as white. Name table strings for this ID specify the user interface strings associated with this palette.
    ,'darkBackgoundPalette': 24 # Dark Backgound Palette. This ID, if used in the CPAL table’s Palette Labels Array, specifies that the corresponding color palette in the CPAL table is appropriate to use with the font when displaying it on a dark background such as black. Name table strings for this ID specify the user interface strings associated with this palette
    ,'variationsPSNamePrefix': 25 # Variations PostScript Name Prefix. If present in a variable font, it may be used as the family prefix in the PostScript Name Generation for Variation Fonts algorithm. The character set is restricted to ASCII-range uppercase Latin letters, lowercase Latin letters, and digits. All name strings for name ID 25 within a font, when converted to ASCII, must be identical. See Adobe Technical Note #5902: “PostScript Name Generation for Variation Fonts” for reasons to include name ID 25 in a font, and for examples. For general information on OpenType Font Variations, see the chapter, OpenType Font Variations Overview.

}

class Names(object):
    def __init__(self, platformID, familyName, weightName, italic, version, vendorID):
        self._familyName = familyName
        self._weightName = weightName
        self._italic = italic
        self._version = version
        self._vendorID = vendorID
        if platformID not in (MAC_ID, WIN_ID):
            raise ValueError('unknown platformID {0}'.format(platformID))
        self.pid = platformID

    # 1
    @property
    def fontFamilyName(self):
        if self.pid == MAC_ID:
            return self._familyName
        elif self.pid == WIN_ID:
            if self._weightName == 'Regular':
                return self._familyName
            else:
                return '{0} {1}'.format(self._familyName, self._weightName)

    # 2
    @property
    def fontSubfamilyName(self):
        if self.pid == MAC_ID:
            if self._italic:
                if self._weightName == 'Regular':
                    return 'Italic'
                return '{0} Italic'.format(self._weightName)
            return self._weightName
        elif self.pid == WIN_ID:
            if self._italic and self._weightName == 'Bold':
                return 'Bold Italic'
            if self._italic:
                return 'Italic'
            if self._weightName == 'Bold':
                return 'Bold'
            return 'Regular'

    # 3
    @property
    def fontIdentifier(self):
        return '{0};{1};{2}'.format(self._version, self._vendorID, self.postscriptName)

    # 4
    @property
    def fullFontName(self):
        if self._weightName == 'Regular':
            name = self._familyName
        else:
            name = '{0} {1}'.format(self._familyName, self._weightName)
        if self._italic:
            name = '{0} Italic'.format(name)
        return name

    # 5
    @property
    def version(self):
        return 'Version {0}'.format(self._version)

    # 6
    @property
    def postscriptName(self):
        familyName = self._familyName.replace(' ', '')
        if self._italic and self._weightName == 'Regular':
            style = 'Italic'
        elif self._italic:
            style = '{0}Italic'.format(self._weightName)
        else:
            style = self._weightName
        return '{0}-{1}'.format(familyName, style)

    #16
    @property
    def typographicFamily(self):
        if self.pid == MAC_ID:
            return None
        elif self.pid == WIN_ID:
            if self._weightName in ('Regular', 'Bold'):
                return None
            return self._familyName

    #17
    @property
    def typographicSubfamily(self):
        if self.pid == MAC_ID:
            return None
        elif self.pid == WIN_ID:
            if self._weightName in ('Regular', 'Bold'):
                return None
            if self._italic:
                return '{0} Italic'.format(self._weightName)
            return self._weightName

# we'll generate these entries
FONT_NAME_KEYS = (
    'fontFamilyName'
  , 'fontSubfamilyName'
  , 'fontIdentifier'
  , 'fullFontName'
  , 'version'
  , 'postscriptName'
  , 'typographicFamily'
  , 'typographicSubfamily'
)

def makeNameEntries(pID, encID, langID, familyName, weightName, italic, version, vendorID):
    result = []
    values = Names(pID, familyName, weightName, italic, version, vendorID)
    for name in FONT_NAME_KEYS:
        data = getattr(values, name)
        if data is None:
            continue
        nameID = NAME_IDS[name]
        result.append([data, nameID, pID, encID, langID])
    return result

def makeNames(win_langID, familyName, weightName, isItalic, version, vendorID):
    names = []
    assert weightName in WEIGHT_NAME_2_WEIGHT_CLASS, \
                    '`weightName` must be one of {0}'.format(
                            ', '.join(WEIGHT_NAME_2_WEIGHT_CLASS.keys()))

    win_encID = PLAT_ENC_IDS[WIN_ID]
    mac_encID = PLAT_ENC_IDS[MAC_ID]
    mac_langID = WIN_LANG_ID_2_MAC_LANG_ID[win_langID]

    names += makeNameEntries(WIN_ID, win_encID, win_langID, familyName
                           , weightName, isItalic, version, vendorID)
    names += makeNameEntries(MAC_ID, mac_encID, mac_langID, familyName
                           , weightName, isItalic, version, vendorID)
    return names

# fsSelection bit definitions:
FSSEL_ITALIC         = (1 << 0)
FSSEL_BOLD           = (1 << 5)
FSSEL_REGULAR        = (1 << 6)

# macStyle bit definitions:
MACSTYLE_BOLD   = (1 << 0)
MACSTYLE_ITALIC = (1 << 1)

def makeOS2(fsSelection, weightName, isItalic, vendorID):
    fsSelection &= FSSEL_ITALIC if isItalic else ~FSSEL_ITALIC
    fsSelection &= FSSEL_BOLD if weightName == 'Bold' else ~FSSEL_BOLD
    fsSelection &= FSSEL_REGULAR if weightName == 'Regular' else ~FSSEL_REGULAR

    return [
        ['achVendID', vendorID]
      , ['usWeightClass', WEIGHT_NAME_2_WEIGHT_CLASS[weightName]]
      , ['fsSelection', fsSelection]
    ]

def makeHead(macStyle, weightName, isItalic):
    macStyle &= MACSTYLE_ITALIC if isItalic else ~MACSTYLE_ITALIC
    macStyle &= MACSTYLE_BOLD if weightName == 'Bold' else ~MACSTYLE_BOLD
    return [
        ['macStyle', macStyle]
    ]
