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
import enum

# =====================================
# GLOBAL CONSTANTS DEFINITIONS

# These variable font naming rules will soon change.
# For more detail, see:
# https://github.com/googlefonts/fontbakery/issues/2396#issuecomment-473250089
VARFONT_SUFFIXES = [
  "VF",
  "Italic-VF",
  "Roman-VF"]

STATIC_STYLE_NAMES = [
  "Thin",
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

RIBBI_STYLE_NAMES = [
  "Regular",
  "Italic",
  "Bold",
  "BoldItalic",
  "Bold Italic"]  # <-- Do we really need this one?

PLACEHOLDER_LICENSING_TEXT = {
  'UFL.txt': 'Licensed under the Ubuntu Font Licence 1.0.',
  'OFL.txt': 'This Font Software is licensed under the SIL Open Font '
             'License, Version 1.1. This license is available with a FAQ '
             'at: http://scripts.sil.org/OFL',
  'LICENSE.txt': 'Licensed under the Apache License, Version 2.0'
}

# ANSI color codes for the helper logging class:
RED_STR = '\033[1;31;40m{}\033[0m'
GREEN_STR = '\033[1;32;40m{}\033[0m'
YELLOW_STR = '\033[1;33;40m{}\033[0m'
BLUE_STR = '\033[1;34;40m{}\033[0m'
CYAN_STR = '\033[1;36;40m{}\033[0m'
WHITE_STR = '\033[1;37;40m{}\033[0m'

class NameID(enum.IntEnum):
  """ nameID definitions for the name table """
  COPYRIGHT_NOTICE = 0
  FONT_FAMILY_NAME = 1
  FONT_SUBFAMILY_NAME = 2
  UNIQUE_FONT_IDENTIFIER = 3
  FULL_FONT_NAME = 4
  VERSION_STRING = 5
  POSTSCRIPT_NAME = 6
  TRADEMARK = 7
  MANUFACTURER_NAME = 8
  DESIGNER = 9
  DESCRIPTION = 10
  VENDOR_URL = 11
  DESIGNER_URL = 12
  LICENSE_DESCRIPTION = 13
  LICENSE_INFO_URL = 14
  # Name ID 15 is RESERVED
  TYPOGRAPHIC_FAMILY_NAME = 16
  TYPOGRAPHIC_SUBFAMILY_NAME = 17
  COMPATIBLE_FULL_MACONLY = 18
  SAMPLE_TEXT = 19
  POSTSCRIPT_CID_NAME = 20
  WWS_FAMILY_NAME = 21
  WWS_SUBFAMILY_NAME = 22
  LIGHT_BACKGROUND_PALETTE = 23
  DARK_BACKGROUD_PALETTE = 24

class FsSelection(enum.IntEnum):
  ITALIC         = (1 << 0)
  UNDERSCORE     = (1 << 1)
  NEGATIVE       = (1 << 2)
  OUTLINED       = (1 << 3)
  STRIKEOUT      = (1 << 4)
  BOLD           = (1 << 5)
  REGULAR        = (1 << 6)
  USETYPOMETRICS = (1 << 7)
  WWS            = (1 << 8)
  OBLIQUE        = (1 << 9)

class MacStyle(enum.IntEnum):
  BOLD   = (1 << 0)
  ITALIC = (1 << 1)

class PANOSE_Proportion(enum.IntEnum):
  ANY = 0
  NO_FIT = 1
  OLD_STYLE = 2
  MODERN = 3
  EVEN_WIDTH = 4
  EXTENDED = 5
  CONDENSED = 6
  VERY_EXTENDED = 7
  VERY_CONDENSED = 8
  MONOSPACED = 9

class IsFixedWidth(enum.IntEnum):
  """ 'post' table / isFixedWidth definitions """
  NOT_MONOSPACED = 0
  # Do NOT use `MONOSPACED = 1` because *any* non-zero value means monospaced.
  # I've commented it out because we were incorrectly testing against it. - CJC

class PlatformID(enum.IntEnum):
  UNICODE = 0
  MACINTOSH = 1
  ISO = 2
  WINDOWS = 3
  CUSTOM = 4

class UnicodeEncodingID(enum.IntEnum):
  """ Unicode platform-specific encoding IDs
      (when platID == 0)
  """
  UNICODE_1_0 = 0
  UNICODE_1_1 = 1
  ISO_IEC_10646 = 2
  UNICODE_2_0_BMP_ONLY = 3
  UNICODE_2_0_FULL = 4
  UNICODE_VARIATION_SEQUENCES = 5
  UNICODE_FULL = 6

class WindowsEncodingID(enum.IntEnum):
  """ Windows platform-specific encoding IDs
      (when platID == 3)
  """
  SYMBOL = 0
  UNICODE_BMP = 1
  SHIFTJIS = 2
  PRC = 3
  BIG5 = 4
  WANSUNG = 5
  JOHAB = 6
  # IDs 7, 8 and 9 are reserved.
  UNICODE_FULL_REPERTOIRE = 10

class PriorityLevel(enum.IntEnum):
  """ Check priority levels """
  TRIVIAL = 4
  LOW = 3
  NORMAL = 2
  IMPORTANT = 1
  CRITICAL = 0  # ON FIRE! Must immediately fix!

ENGLISH_LANG_ID = 0x0409
