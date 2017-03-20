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
                     "BoldItalic",
                     "Bold Italic"]  # <-- Do we really need this one?

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

WEIGHT_VALUE_TO_NAME = {
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
# FIXME: Shouldn't the two dicts above be merged into a single
#        one and have code refactored to use the single source
#        of numerical value to weight name ?

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
    'OFL.txt': u'This Font Software is licensed under the SIL Open Font '
               'License, Version 1.1. This license is available with a FAQ '
               'at: http://scripts.sil.org/OFL',
    'LICENSE.txt': u'Licensed under the Apache License, Version 2.0'
}

LICENSE_URL = {
    'OFL.txt': u'http://scripts.sil.org/OFL',
    'LICENSE.txt': u'http://www.apache.org/licenses/LICENSE-2.0'
}

LICENSE_NAME = {
    'OFL.txt': u'Open Font',
    'LICENSE.txt': u'Apache'
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

# =====================================
# Check priority levels:
TRIVIAL = 4
LOW = 3
NORMAL = 2
IMPORTANT = 1
CRITICAL = 0  # ON FIRE! Must immediately fix!
