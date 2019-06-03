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

WIN_ENGLISH_LANG_ID = 0x0409
MAC_ROMAN_LANG_ID = 0x0

GF_latin_core = {
  #  NULL
  0x000D: (None, "CARRIAGE RETURN"),
  0x0020: (" ", "SPACE"),
  0x0021: ("!", "EXCLAMATION MARK"),
  0x0022: ("\"", "QUOTATION MARK"),
  0x0023: ("#", "NUMBER SIGN"),
  0x0024: ("$", "DOLLAR SIGN"),
  0x0025: ("%", "PERCENT SIGN"),
  0x0026: ("&", "AMPERSAND"),
  0x0027: ("'", "APOSTROPHE"),
  0x0028: ("(", "LEFT PARENTHESIS"),
  0x0029: (")", "RIGHT PARENTHESIS"),
  0x002A: ("*", "ASTERISK"),
  0x002B: ("+", "PLUS SIGN"),
  0x002C: (",", "COMMA"),
  0x002D: ("-", "HYPHEN-MINUS"),
  0x002E: (".", "FULL STOP"),
  0x002F: ("/", "SOLIDUS"),
  0x0030: ("0", "DIGIT ZERO"),
  0x0031: ("1", "DIGIT ONE"),
  0x0032: ("2", "DIGIT TWO"),
  0x0033: ("3", "DIGIT THREE"),
  0x0034: ("4", "DIGIT FOUR"),
  0x0035: ("5", "DIGIT FIVE"),
  0x0036: ("6", "DIGIT SIX"),
  0x0037: ("7", "DIGIT SEVEN"),
  0x0038: ("8", "DIGIT EIGHT"),
  0x0039: ("9", "DIGIT NINE"),
  0x003A: (":", "COLON"),
  0x003B: (";", "SEMICOLON"),
  0x003C: ("<", "LESS-THAN SIGN"),
  0x003D: ("=", "EQUALS SIGN"),
  0x003E: (">", "GREATER-THAN SIGN"),
  0x003F: ("?", "QUESTION MARK"),
  0x0040: ("@", "COMMERCIAL AT"),
  0x0041: ("A", "LATIN CAPITAL LETTER A"),
  0x0042: ("B", "LATIN CAPITAL LETTER B"),
  0x0043: ("C", "LATIN CAPITAL LETTER C"),
  0x0044: ("D", "LATIN CAPITAL LETTER D"),
  0x0045: ("E", "LATIN CAPITAL LETTER E"),
  0x0046: ("F", "LATIN CAPITAL LETTER F"),
  0x0047: ("G", "LATIN CAPITAL LETTER G"),
  0x0048: ("H", "LATIN CAPITAL LETTER H"),
  0x0049: ("I", "LATIN CAPITAL LETTER I"),
  0x004A: ("J", "LATIN CAPITAL LETTER J"),
  0x004B: ("K", "LATIN CAPITAL LETTER K"),
  0x004C: ("L", "LATIN CAPITAL LETTER L"),
  0x004D: ("M", "LATIN CAPITAL LETTER M"),
  0x004E: ("N", "LATIN CAPITAL LETTER N"),
  0x004F: ("O", "LATIN CAPITAL LETTER O"),
  0x0050: ("P", "LATIN CAPITAL LETTER P"),
  0x0051: ("Q", "LATIN CAPITAL LETTER Q"),
  0x0052: ("R", "LATIN CAPITAL LETTER R"),
  0x0053: ("S", "LATIN CAPITAL LETTER S"),
  0x0054: ("T", "LATIN CAPITAL LETTER T"),
  0x0055: ("U", "LATIN CAPITAL LETTER U"),
  0x0056: ("V", "LATIN CAPITAL LETTER V"),
  0x0057: ("W", "LATIN CAPITAL LETTER W"),
  0x0058: ("X", "LATIN CAPITAL LETTER X"),
  0x0059: ("Y", "LATIN CAPITAL LETTER Y"),
  0x005A: ("Z", "LATIN CAPITAL LETTER Z"),
  0x005B: ("[", "LEFT SQUARE BRACKET"),
  0x005C: ("\\", "REVERSE SOLIDUS"),
  0x005D: ("]", "RIGHT SQUARE BRACKET"),
  0x005E: ("^", "CIRCUMFLEX ACCENT"),
  0x005F: ("_", "LOW LINE"),
  0x0060: ("`", "GRAVE ACCENT"),
  0x0061: ("a", "LATIN SMALL LETTER A"),
  0x0062: ("b", "LATIN SMALL LETTER B"),
  0x0063: ("c", "LATIN SMALL LETTER C"),
  0x0064: ("d", "LATIN SMALL LETTER D"),
  0x0065: ("e", "LATIN SMALL LETTER E"),
  0x0066: ("f", "LATIN SMALL LETTER F"),
  0x0067: ("g", "LATIN SMALL LETTER G"),
  0x0068: ("h", "LATIN SMALL LETTER H"),
  0x0069: ("i", "LATIN SMALL LETTER I"),
  0x006A: ("j", "LATIN SMALL LETTER J"),
  0x006B: ("k", "LATIN SMALL LETTER K"),
  0x006C: ("l", "LATIN SMALL LETTER L"),
  0x006D: ("m", "LATIN SMALL LETTER M"),
  0x006E: ("n", "LATIN SMALL LETTER N"),
  0x006F: ("o", "LATIN SMALL LETTER O"),
  0x0070: ("p", "LATIN SMALL LETTER P"),
  0x0071: ("q", "LATIN SMALL LETTER Q"),
  0x0072: ("r", "LATIN SMALL LETTER R"),
  0x0073: ("s", "LATIN SMALL LETTER S"),
  0x0074: ("t", "LATIN SMALL LETTER T"),
  0x0075: ("u", "LATIN SMALL LETTER U"),
  0x0076: ("v", "LATIN SMALL LETTER V"),
  0x0077: ("w", "LATIN SMALL LETTER W"),
  0x0078: ("x", "LATIN SMALL LETTER X"),
  0x0079: ("y", "LATIN SMALL LETTER Y"),
  0x007A: ("z", "LATIN SMALL LETTER Z"),
  0x007B: ("{", "LEFT CURLY BRACKET"),
  0x007C: ("|", "VERTICAL LINE"),
  0x007D: ("}", "RIGHT CURLY BRACKET"),
  0x007E: ("~", "TILDE"),
  0x00A0: (" ", "NO-BREAK SPACE"),
  0x00A1: ("¡", "INVERTED EXCLAMATION MARK"),
  0x00A2: ("¢", "CENT SIGN"),
  0x00A3: ("£", "POUND SIGN"),
  0x00A4: ("¤", "CURRENCY SIGN"),
  0x00A5: ("¥", "YEN SIGN"),
  0x00A6: ("¦", "BROKEN BAR"),
  0x00A7: ("§", "SECTION SIGN"),
  0x00A8: ("¨", "DIAERESIS"),
  0x00A9: ("©", "COPYRIGHT SIGN"),
  0x00AA: ("ª", "FEMININE ORDINAL INDICATOR"),
  0x00AB: ("«", "LEFT-POINTING DOUBLE ANGLE QUOTATION MARK"),
  0x00AC: ("¬", "NOT SIGN"),
  0x00AD: ("­", "SOFT HYPHEN"),
  0x00AE: ("®", "REGISTERED SIGN"),
  0x00AF: ("¯", "MACRON"),
  0x00B0: ("°", "DEGREE SIGN"),
  0x00B1: ("±", "PLUS-MINUS SIGN"),
  0x00B2: ("²", "SUPERSCRIPT TWO"),
  0x00B3: ("³", "SUPERSCRIPT THREE"),
  0x00B4: ("´", "ACUTE ACCENT"),
  0x00B5: ("µ", "MICRO SIGN"),
  0x00B6: ("¶", "PILCROW SIGN"),
  0x00B7: ("·", "MIDDLE DOT"),
  0x00B8: ("¸", "CEDILLA"),
  0x00B9: ("¹", "SUPERSCRIPT ONE"),
  0x00BA: ("º", "MASCULINE ORDINAL INDICATOR"),
  0x00BB: ("»", "RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK"),
  0x00BC: ("¼", "VULGAR FRACTION ONE QUARTER"),
  0x00BD: ("½", "VULGAR FRACTION ONE HALF"),
  0x00BE: ("¾", "VULGAR FRACTION THREE QUARTERS"),
  0x00BF: ("¿", "INVERTED QUESTION MARK"),
  0x00C0: ("À", "LATIN CAPITAL LETTER A WITH GRAVE"),
  0x00C1: ("Á", "LATIN CAPITAL LETTER A WITH ACUTE"),
  0x00C2: ("Â", "LATIN CAPITAL LETTER A WITH CIRCUMFLEX"),
  0x00C3: ("Ã", "LATIN CAPITAL LETTER A WITH TILDE"),
  0x00C4: ("Ä", "LATIN CAPITAL LETTER A WITH DIAERESIS"),
  0x00C5: ("Å", "LATIN CAPITAL LETTER A WITH RING ABOVE"),
  0x00C6: ("Æ", "LATIN CAPITAL LETTER AE"),
  0x00C7: ("Ç", "LATIN CAPITAL LETTER C WITH CEDILLA"),
  0x00C8: ("È", "LATIN CAPITAL LETTER E WITH GRAVE"),
  0x00C9: ("É", "LATIN CAPITAL LETTER E WITH ACUTE"),
  0x00CA: ("Ê", "LATIN CAPITAL LETTER E WITH CIRCUMFLEX"),
  0x00CB: ("Ë", "LATIN CAPITAL LETTER E WITH DIAERESIS"),
  0x00CC: ("Ì", "LATIN CAPITAL LETTER I WITH GRAVE"),
  0x00CD: ("Í", "LATIN CAPITAL LETTER I WITH ACUTE"),
  0x00CE: ("Î", "LATIN CAPITAL LETTER I WITH CIRCUMFLEX"),
  0x00CF: ("Ï", "LATIN CAPITAL LETTER I WITH DIAERESIS"),
  0x00D0: ("Ð", "LATIN CAPITAL LETTER ETH"),
  0x00D1: ("Ñ", "LATIN CAPITAL LETTER N WITH TILDE"),
  0x00D2: ("Ò", "LATIN CAPITAL LETTER O WITH GRAVE"),
  0x00D3: ("Ó", "LATIN CAPITAL LETTER O WITH ACUTE"),
  0x00D4: ("Ô", "LATIN CAPITAL LETTER O WITH CIRCUMFLEX"),
  0x00D5: ("Õ", "LATIN CAPITAL LETTER O WITH TILDE"),
  0x00D6: ("Ö", "LATIN CAPITAL LETTER O WITH DIAERESIS"),
  0x00D7: ("×", "MULTIPLICATION SIGN"),
  0x00D8: ("Ø", "LATIN CAPITAL LETTER O WITH STROKE"),
  0x00D9: ("Ù", "LATIN CAPITAL LETTER U WITH GRAVE"),
  0x00DA: ("Ú", "LATIN CAPITAL LETTER U WITH ACUTE"),
  0x00DB: ("Û", "LATIN CAPITAL LETTER U WITH CIRCUMFLEX"),
  0x00DC: ("Ü", "LATIN CAPITAL LETTER U WITH DIAERESIS"),
  0x00DD: ("Ý", "LATIN CAPITAL LETTER Y WITH ACUTE"),
  0x00DE: ("Þ", "LATIN CAPITAL LETTER THORN"),
  0x00DF: ("ß", "LATIN SMALL LETTER SHARP S"),
  0x00E0: ("à", "LATIN SMALL LETTER A WITH GRAVE"),
  0x00E1: ("á", "LATIN SMALL LETTER A WITH ACUTE"),
  0x00E2: ("â", "LATIN SMALL LETTER A WITH CIRCUMFLEX"),
  0x00E3: ("ã", "LATIN SMALL LETTER A WITH TILDE"),
  0x00E4: ("ä", "LATIN SMALL LETTER A WITH DIAERESIS"),
  0x00E5: ("å", "LATIN SMALL LETTER A WITH RING ABOVE"),
  0x00E6: ("æ", "LATIN SMALL LETTER AE"),
  0x00E7: ("ç", "LATIN SMALL LETTER C WITH CEDILLA"),
  0x00E8: ("è", "LATIN SMALL LETTER E WITH GRAVE"),
  0x00E9: ("é", "LATIN SMALL LETTER E WITH ACUTE"),
  0x00EA: ("ê", "LATIN SMALL LETTER E WITH CIRCUMFLEX"),
  0x00EB: ("ë", "LATIN SMALL LETTER E WITH DIAERESIS"),
  0x00EC: ("ì", "LATIN SMALL LETTER I WITH GRAVE"),
  0x00ED: ("í", "LATIN SMALL LETTER I WITH ACUTE"),
  0x00EE: ("î", "LATIN SMALL LETTER I WITH CIRCUMFLEX"),
  0x00EF: ("ï", "LATIN SMALL LETTER I WITH DIAERESIS"),
  0x00F0: ("ð", "LATIN SMALL LETTER ETH"),
  0x00F1: ("ñ", "LATIN SMALL LETTER N WITH TILDE"),
  0x00F2: ("ò", "LATIN SMALL LETTER O WITH GRAVE"),
  0x00F3: ("ó", "LATIN SMALL LETTER O WITH ACUTE"),
  0x00F4: ("ô", "LATIN SMALL LETTER O WITH CIRCUMFLEX"),
  0x00F5: ("õ", "LATIN SMALL LETTER O WITH TILDE"),
  0x00F6: ("ö", "LATIN SMALL LETTER O WITH DIAERESIS"),
  0x00F7: ("÷", "DIVISION SIGN"),
  0x00F8: ("ø", "LATIN SMALL LETTER O WITH STROKE"),
  0x00F9: ("ù", "LATIN SMALL LETTER U WITH GRAVE"),
  0x00FA: ("ú", "LATIN SMALL LETTER U WITH ACUTE"),
  0x00FB: ("û", "LATIN SMALL LETTER U WITH CIRCUMFLEX"),
  0x00FC: ("ü", "LATIN SMALL LETTER U WITH DIAERESIS"),
  0x00FD: ("ý", "LATIN SMALL LETTER Y WITH ACUTE"),
  0x00FE: ("þ", "LATIN SMALL LETTER THORN"),
  0x00FF: ("ÿ", "LATIN SMALL LETTER Y WITH DIAERESIS"),
  0x0131: ("ı", "LATIN SMALL LETTER DOTLESS I"),
  0x0152: ("Œ", "LATIN CAPITAL LIGATURE OE"),
  0x0153: ("œ", "LATIN SMALL LIGATURE OE"),
  0x02C6: ("ˆ", "MODIFIER LETTER CIRCUMFLEX ACCENT"),
  0x02DA: ("˚", "RING ABOVE"),
  0x02DC: ("˜", "SMALL TILDE"),
  0x2013: ("–", "EN DASH"),
  0x2014: ("—", "EM DASH"),
  0x2018: ("‘", "LEFT SINGLE QUOTATION MARK"),
  0x2019: ("’", "RIGHT SINGLE QUOTATION MARK"),
  0x201A: ("‚", "SINGLE LOW-9 QUOTATION MARK"),
  0x201C: ("“", "LEFT DOUBLE QUOTATION MARK"),
  0x201D: ("”", "RIGHT DOUBLE QUOTATION MARK"),
  0x201E: ("„", "DOUBLE LOW-9 QUOTATION MARK"),
  0x2022: ("•", "BULLET"),
  0x2026: ("…", "HORIZONTAL ELLIPSIS"),
  0x2039: ("‹", "SINGLE LEFT-POINTING ANGLE QUOTATION MARK"),
  0x203A: ("›", "SINGLE RIGHT-POINTING ANGLE QUOTATION MARK"),
  0x2044: ("⁄", "FRACTION SLASH"),
  0x2074: ("⁴", "SUPERSCRIPT FOUR"),
  0x20AC: ("€", "EURO SIGN"),
  0x2212: ("−", "MINUS SIGN"),
  0x2215: ("∕", "DIVISION SLASH"),
  # 0xE0FF: ("", "PRIVATE USE AREA U+E0FF"),
  # 0xEFFD: ("", "PRIVATE USE AREA U+EFFD"),
  # 0xF000: ("", "PRIVATE USE AREA U+F000"),
}
