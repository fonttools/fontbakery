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
             'at: https://scripts.sil.org/OFL',
  'LICENSE.txt': 'Licensed under the Apache License, Version 2.0'
}

SHOW_GF_DOCS_MSG = (
  "Check has either failed or produced a warning. See our wip spec for "
  "further info https://gist.github.com/m4rc1e/"
  "8f4c4498519e8a36cd54e16a004275cb"
)

# ANSI color codes for the helper logging class:
def color(bg, fg, bold=False):
  bold_bit = 0
  if bold:
    bold_bit = 1
  return ('\033[{};{};{}m'.format(bold_bit, bg, fg+10) + '{}\033[0m').format

def no_color(s):
  return s

BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37
BRIGHT_BLACK = 90
BRIGHT_RED = 91
BRIGHT_GREEN = 92
BRIGHT_YELLOW = 93
BRIGHT_BLUE = 94
BRIGHT_MAGENTA = 95
BRIGHT_CYAN = 96
BRIGHT_WHITE = 97

NO_COLORS_THEME = {
                    "header": no_color,
                       "url": no_color,
                  "check-id": no_color,
               "description": no_color,
           "rationale-title": no_color,
            "rationale-text": no_color,
                      "INFO": no_color,
                      "WARN": no_color,
                     "ERROR": no_color,
                      "SKIP": no_color,
                      "PASS": no_color,
                      "FAIL": no_color,
                   "cupcake": no_color,
                   "spinner": no_color,
      "list-checks: section": no_color,
     "list-checks: check-id": no_color,
  "list-checks: description": no_color
}

DARK_THEME = {                #     Foreground    Background
                    "header": color(WHITE,        BLACK,        bold=True),
                       "url": color(CYAN,         BLACK,        bold=True),
                  "check-id": color(CYAN,         BLACK,        bold=True),
               "description": color(MAGENTA,      BLACK),
           "rationale-title": color(BRIGHT_CYAN,  BRIGHT_BLACK, bold=True),
            "rationale-text": color(WHITE,        BLACK),
                      "INFO": color(CYAN,         BLACK),
                      "WARN": color(YELLOW,       BLACK),
                     "ERROR": color(BRIGHT_WHITE, RED),
                      "SKIP": color(BLUE,         BLACK),
                      "PASS": color(GREEN,        BLACK),
                      "FAIL": color(RED,          BLACK),
                   "cupcake": color(MAGENTA,      BLACK),
                   "spinner": color(GREEN,        BLACK),
      "list-checks: section": color(WHITE,        BLACK),
     "list-checks: check-id": color(CYAN,         BLACK),
  "list-checks: description": color(BLUE,         BLACK)
}

LIGHT_THEME = {               #     Foreground     Background
                    "header": color(BLACK,         BRIGHT_WHITE,  bold=True),
                       "url": color(CYAN,          BRIGHT_WHITE,  bold=True),
                  "check-id": color(MAGENTA,       BRIGHT_WHITE,  bold=True),
               "description": color(CYAN,          BRIGHT_WHITE),
           "rationale-title": color(MAGENTA,       BRIGHT_WHITE,  bold=True),
            "rationale-text": color(BLACK,         BRIGHT_WHITE),
                      "INFO": color(CYAN,          BRIGHT_WHITE),
                      "WARN": color(BLACK,         BRIGHT_YELLOW, bold=True),
                     "ERROR": color(BRIGHT_WHITE,  BRIGHT_RED,    bold=True),
                      "SKIP": color(BLUE,          BRIGHT_WHITE),
                      "PASS": color(GREEN,         BRIGHT_WHITE),
                      "FAIL": color(BRIGHT_RED,    BRIGHT_WHITE,  bold=True),
                   "cupcake": color(MAGENTA,       BRIGHT_WHITE),
                   "spinner": color(GREEN,         BRIGHT_WHITE),
      "list-checks: section": color(WHITE,         BRIGHT_WHITE,  bold=True),
     "list-checks: check-id": color(CYAN,          BRIGHT_WHITE,  bold=True),
  "list-checks: description": color(BLUE,          BRIGHT_WHITE)
}


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

class GlyphClass(enum.IntEnum):
  BASE = 1
  LIGATURE = 2
  MARK = 3
  COMPONENT = 4

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
  UNICODE_2_0_BMP_ONLY = 3 # Basic Multilingual Plane
  UNICODE_2_0_FULL = 4
  UNICODE_VARIATION_SEQUENCES = 5
  UNICODE_FULL = 6

class MacintoshEncodingID(enum.IntEnum):
  """ Encoding IDs defined for use
      with the Macintosh platform
      (when platID = 1)
  """
  ROMAN = 0
  JAPANESE = 1
  CHINESE_TRADITIONAL = 2
  KOREAN = 3
  ARABIC = 4
  HEBREW = 5
  GREEK = 6
  RUSSIAN = 7
  RSYMBOL = 8
  DEVANAGARI = 9
  GURMUKHI = 10
  GUJARATI = 11
  ORIYA = 12
  BENGALI = 13
  TAMIL = 14
  TELUGU = 15
  KANNADA = 16
  MALAYALAM = 17
  SINHALESE = 18
  BURMESE = 19
  KHMER = 20
  THAI = 21
  LAOTIAN = 22
  GEORGIAN = 23
  ARMENIAN = 24
  CHINESE_SIMPLIFIED = 25
  TIBETAN = 26
  MONGOLIAN = 27
  GEEZ = 28
  SLAVIC = 29
  VIETNAMESE = 30
  SINDHI = 31
  UNINTERPRETED = 32

class WindowsEncodingID(enum.IntEnum):
  """ Windows platform-specific encoding IDs
      (when platID == 3)
  """
  SYMBOL = 0
  UNICODE_BMP = 1 # Basic Multilingual Plane
  SHIFTJIS = 2
  PRC = 3
  BIG5 = 4
  WANSUNG = 5
  JOHAB = 6
  # IDs 7, 8 and 9 are reserved.
  UNICODE_FULL_REPERTOIRE = 10

class MacintoshLanguageID(enum.IntEnum):
  """ Platform-specific Language IDs
      assigned by Apple
  """
  ENGLISH = 0

class WindowsLanguageID(enum.IntEnum):
  """ Platform-specific Language IDs
      assigned by Microsoft
  """
  ENGLISH_USA = 0x0409


class PriorityLevel(enum.IntEnum):
  """ Check priority levels """
  TRIVIAL = 4
  LOW = 3
  NORMAL = 2
  IMPORTANT = 1
  CRITICAL = 0  # ON FIRE! Must immediately fix!


GF_latin_core = {
  #  NULL
  # 0x000D: (None, "CARRIAGE RETURN"),
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


# https://docs.microsoft.com/en-us/typography/opentype/spec/os2
UNICODERANGE_DATA = [
  [(0, "Basic Latin",                               0x00000, 0x0007F)],
  [(1, "Latin-1 Supplement",                        0x00080, 0x000FF)],
  [(2, "Latin Extended-A",                          0x00100, 0x0017F)],
  [(3, "Latin Extended-B",                          0x00180, 0x0024F)],

  [(4, "IPA Extensions",                           0x00250, 0x002AF),
   (4, "Phonetic Extensions",                      0x01D00, 0x01D7F),
   (4, "Phonetic Extensions Supplement",           0x01D80, 0x01DBF)],

  [(5, "Spacing Modifier Letters",                 0x002B0, 0x002FF),
   (5, "Modifier Tone Letters",                    0x0A700, 0x0A71F)],

  [(6, "Combining Diacritical Marks",              0x00300, 0x0036F),
   (6, "Combining Diacritical Marks Supplement",   0x01DC0, 0x01DFF)],

  [(7, "Greek and Coptic",                          0x00370, 0x003FF)],
  [(8, "Coptic",                                    0x02C80, 0x02CFF)],

  [(9, "Cyrillic",                                 0x00400, 0x004FF),
   (9, "Cyrillic Supplement",                      0x00500, 0x0052F),
   (9, "Cyrillic Extended-A",                      0x02DE0, 0x02DFF),
   (9, "Cyrillic Extended-B",                      0x0A640, 0x0A69F)],

  [(10, "Armenian",                                 0x00530, 0x0058F)],
  [(11, "Hebrew",                                   0x00590, 0x005FF)],
  [(12, "Vai",                                      0x0A500, 0x0A63F)],

  [(13, "Arabic",                                  0x00600, 0x006FF),
   (13, "Arabic Supplement",                       0x00750, 0x0077F)],

  [(14, "NKo",                                      0x007C0, 0x007FF)],
  [(15, "Devanagari",                               0x00900, 0x0097F)],
  [(16, "Bengali",                                  0x00980, 0x009FF)],
  [(17, "Gurmukhi",                                 0x00A00, 0x00A7F)],
  [(18, "Gujarati",                                 0x00A80, 0x00AFF)],
  [(19, "Oriya",                                    0x00B00, 0x00B7F)],
  [(20, "Tamil",                                    0x00B80, 0x00BFF)],
  [(21, "Telugu",                                   0x00C00, 0x00C7F)],
  [(22, "Kannada",                                  0x00C80, 0x00CFF)],
  [(23, "Malayalam",                                0x00D00, 0x00D7F)],
  [(24, "Thai",                                     0x00E00, 0x00E7F)],
  [(25, "Lao",                                      0x00E80, 0x00EFF)],

  [(26, "Georgian",                                0x010A0, 0x010FF),
   (26, "Georgian Supplement",                     0x02D00, 0x02D2F)],

  [(27, "Balinese",                                 0x01B00, 0x01B7F)],
  [(28, "Hangul Jamo",                              0x01100, 0x011FF)],

  [(29, "Latin Extended Additional",               0x01E00, 0x01EFF),
   (29, "Latin Extended-C",                        0x02C60, 0x02C7F),
   (29, "Latin Extended-D",                        0x0A720, 0x0A7FF)],

  [(30, "Greek Extended",                           0x01F00, 0x01FFF)],

  [(31, "General Punctuation",                     0x02000, 0x0206F),
   (31, "Supplemental Punctuation",                0x02E00, 0x02E7F)],

  [(32, "Superscripts And Subscripts",              0x02070, 0x0209F)],
  [(33, "Currency Symbols",                         0x020A0, 0x020CF)],
  [(34, "Combining Diacritical Marks For Symbols",  0x020D0, 0x020FF)],
  [(35, "Letterlike Symbols",                       0x02100, 0x0214F)],
  [(36, "Number Forms",                             0x02150, 0x0218F)],

  [(37, "Arrows",                                  0x02190, 0x021FF),
   (37, "Supplemental Arrows-A",                   0x027F0, 0x027FF),
   (37, "Supplemental Arrows-B",                   0x02900, 0x0297F),
   (37, "Miscellaneous Symbols and Arrows",        0x02B00, 0x02BFF)],

  [(38, "Mathematical Operators",                  0x02200, 0x022FF),
   (38, "Supplemental Mathematical Operators",     0x02A00, 0x02AFF),
   (38, "Miscellaneous Mathematical Symbols-A",    0x027C0, 0x027EF),
   (38, "Miscellaneous Mathematical Symbols-B",    0x02980, 0x029FF)],

  [(39, "Miscellaneous Technical",                  0x02300, 0x023FF)],
  [(40, "Control Pictures",                         0x02400, 0x0243F)],
  [(41, "Optical Character Recognition",            0x02440, 0x0245F)],
  [(42, "Enclosed Alphanumerics",                   0x02460, 0x024FF)],
  [(43, "Box Drawing",                              0x02500, 0x0257F)],
  [(44, "Block Elements",                           0x02580, 0x0259F)],
  [(45, "Geometric Shapes",                         0x025A0, 0x025FF)],
  [(46, "Miscellaneous Symbols",                    0x02600, 0x026FF)],
  [(47, "Dingbats",                                 0x02700, 0x027BF)],
  [(48, "CJK Symbols And Punctuation",              0x03000, 0x0303F)],
  [(49, "Hiragana",                                 0x03040, 0x0309F)],

  [(50, "Katakana",                                0x030A0, 0x030FF),
   (50, "Katakana Phonetic Extensions",            0x031F0, 0x031FF)],

  [(51, "Bopomofo",                                0x03100, 0x0312F),
   (51, "Bopomofo Extended",                       0x031A0, 0x031BF)],

  [(52, "Hangul Compatibility Jamo",                0x03130, 0x0318F)],
  [(53, "Phags-pa",                                 0x0A840, 0x0A87F)],
  [(54, "Enclosed CJK Letters And Months",          0x03200, 0x032FF)],
  [(55, "CJK Compatibility",                        0x03300, 0x033FF)],
  [(56, "Hangul Syllables",                         0x0AC00, 0x0D7AF)],
  [(57, "Non-Plane 0 *",                            0x0D800, 0x0DFFF)],
  [(58, "Phoenician",                               0x10900, 0x1091F)],

  [(59, "CJK Unified Ideographs",                  0x04E00, 0x09FFF),
   (59, "CJK Radicals Supplement",                 0x02E80, 0x02EFF),
   (59, "Kangxi Radicals",                         0x02F00, 0x02FDF),
   (59, "Ideographic Description Characters",      0x02FF0, 0x02FFF),
   (59, "CJK Unified Ideographs Extension A",      0x03400, 0x04DBF),
   (59, "CJK Unified Ideographs Extension B",      0x20000, 0x2A6DF),
   (59, "Kanbun",                                  0x03190, 0x0319F)],

  [(60, "Private Use Area (plane 0)",               0x0E000, 0x0F8FF)],

  [(61, "CJK Strokes",                             0x031C0, 0x031EF),
   (61, "CJK Compatibility Ideographs",            0x0F900, 0x0FAFF),
   (61, "CJK Compatibility Ideographs Supplement", 0x2F800, 0x2FA1F)],

  [(62, "Alphabetic Presentation Forms",            0x0FB00, 0x0FB4F)],
  [(63, "Arabic Presentation Forms-A",              0x0FB50, 0x0FDFF)],
  [(64, "Combining Half Marks",                     0x0FE20, 0x0FE2F)],

  [(65, "Vertical Forms",                          0x0FE10, 0x0FE1F),
   (65, "CJK Compatibility Forms",                 0x0FE30, 0x0FE4F)],

  [(66, "Small Form Variants",                      0x0FE50, 0x0FE6F)],
  [(67, "Arabic Presentation Forms-B",              0x0FE70, 0x0FEFF)],
  [(68, "Halfwidth And Fullwidth Forms",            0x0FF00, 0x0FFEF)],
  [(69, "Specials",                                 0x0FFF0, 0x0FFFF)],
  [(70, "Tibetan",                                  0x00F00, 0x00FFF)],
  [(71, "Syriac",                                   0x00700, 0x0074F)],
  [(72, "Thaana",                                   0x00780, 0x007BF)],
  [(73, "Sinhala",                                  0x00D80, 0x00DFF)],
  [(74, "Myanmar",                                  0x01000, 0x0109F)],

  [(75, "Ethiopic",                                0x01200, 0x0137F),
   (75, "Ethiopic Supplement",                     0x01380, 0x0139F),
   (75, "Ethiopic Extended",                       0x02D80, 0x02DDF)],

  [(76, "Cherokee",                                 0x013A0, 0x013FF)],
  [(77, "Unified Canadian Aboriginal Syllabics",    0x01400, 0x0167F)],
  [(78, "Ogham",                                    0x01680, 0x0169F)],
  [(79, "Runic",                                    0x016A0, 0x016FF)],

  [(80, "Khmer",                                   0x01780, 0x017FF),
   (80, "Khmer Symbols",                           0x019E0, 0x019FF)],

  [(81, "Mongolian",                                0x01800, 0x018AF)],
  [(82, "Braille Patterns",                         0x02800, 0x028FF)],

  [(83, "Yi Syllables",                            0x0A000, 0x0A48F),
   (83, "Yi Radicals",                             0x0A490, 0x0A4CF)],

  [(84, "Tagalog",                                 0x01700, 0x0171F),
   (84, "Hanunoo",                                 0x01720, 0x0173F),
   (84, "Buhid",                                   0x01740, 0x0175F),
   (84, "Tagbanwa",                                0x01760, 0x0177F)],

  [(85, "Old Italic",                               0x10300, 0x1032F)],
  [(86, "Gothic",                                   0x10330, 0x1034F)],
  [(87, "Deseret",                                  0x10400, 0x1044F)],

  [(88, "Byzantine Musical Symbols",               0x1D000, 0x1D0FF),
   (88, "Musical Symbols",                         0x1D100, 0x1D1FF),
   (88, "Ancient Greek Musical Notation",          0x1D200, 0x1D24F)],

  [(89, "Mathematical Alphanumeric Symbols",        0x1D400, 0x1D7FF)],

  [(90, "Private Use (plane 15)",                  0xFF000, 0xFFFFD),
   (90, "Private Use (plane 16)",                 0x100000, 0x10FFFD)],

  [(91, "Variation Selectors",                     0x0FE00, 0x0FE0F),
   (91, "Variation Selectors Supplement",          0xE0100, 0xE01EF)],

  [(92, "Tags",                                     0xE0000, 0xE007F)],
  [(93, "Limbu",                                    0x01900, 0x0194F)],
  [(94, "Tai Le",                                   0x01950, 0x0197F)],
  [(95, "New Tai Lue",                              0x01980, 0x019DF)],
  [(96, "Buginese",                                 0x01A00, 0x01A1F)],
  [(97, "Glagolitic",                               0x02C00, 0x02C5F)],
  [(98, "Tifinagh",                                 0x02D30, 0x02D7F)],
  [(99, "Yijing Hexagram Symbols",                  0x04DC0, 0x04DFF)],
  [(100, "Syloti Nagri",                            0x0A800, 0x0A82F)],

  [(101, "Linear B Syllabary",                     0x10000, 0x1007F),
   (101, "Linear B Ideograms",                     0x10080, 0x100FF),
   (101, "Aegean Numbers",                         0x10100, 0x1013F)],

  [(102, "Ancient Greek Numbers",                   0x10140, 0x1018F)],
  [(103, "Ugaritic",                                0x10380, 0x1039F)],
  [(104, "Old Persian",                             0x103A0, 0x103DF)],
  [(105, "Shavian",                                 0x10450, 0x1047F)],
  [(106, "Osmanya",                                 0x10480, 0x104AF)],
  [(107, "Cypriot Syllabary",                       0x10800, 0x1083F)],
  [(108, "Kharoshthi",                              0x10A00, 0x10A5F)],
  [(109, "Tai Xuan Jing Symbols",                   0x1D300, 0x1D35F)],

  [(110, "Cuneiform",                              0x12000, 0x123FF),
   (110, "Cuneiform Numbers and Punctuation",      0x12400, 0x1247F)],

  [(111, "Counting Rod Numerals",                   0x1D360, 0x1D37F)],
  [(112, "Sundanese",                               0x01B80, 0x01BBF)],
  [(113, "Lepcha",                                  0x01C00, 0x01C4F)],
  [(114, "Ol Chiki",                                0x01C50, 0x01C7F)],
  [(115, "Saurashtra",                              0x0A880, 0x0A8DF)],
  [(116, "Kayah Li",                                0x0A900, 0x0A92F)],
  [(117, "Rejang",                                  0x0A930, 0x0A95F)],
  [(118, "Cham",                                    0x0AA00, 0x0AA5F)],
  [(119, "Ancient Symbols",                         0x10190, 0x101CF)],
  [(120, "Phaistos Disc",                           0x101D0, 0x101FF)],

  [(121, "Carian",                                 0x102A0, 0x102DF),
   (121, "Lycian",                                 0x10280, 0x1029F),
   (121, "Lydian",                                 0x10920, 0x1093F)],

  [(122, "Domino Tiles",                           0x1F030, 0x1F09F),
   (122, "Mahjong Tiles",                          0x1F000, 0x1F02F)]
]


CJK_CODEPAGE_BITS = {
  "JIS/Japan": 17,
  "Chinese: Simplified chars—PRC and Singapore": 18,
  "Korean Wansung": 19,
  "Chinese: Traditional chars—Taiwan and Hong Kong": 20,
  "Korean Johab": 21
}


# FIXME: This is a bit redundant with UNICODERANGE_DATA:
CJK_UNICODE_RANGE_BITS = {
  'Hangul Jamo': 28,
  #  'CJK Symbols And Punctuation': 48,
  'Hiragana': 49,
  'Katakana': 50,
  'Bopomofo': 51,
  'Hangul Compatibility Jamo': 52,
  'Enclosed CJK Letters And Months': 54,
  'CJK Compatibility': 55,
  'Hangul Syllables': 56,
  'CJK Unified Ideographs': 59,
  'CJK Strokes': 61,
  'Yi Syllables': 83
}


# FIXME: This is a bit redundant with UNICODERANGE_DATA:
CJK_UNICODE_RANGES = [
  [0x1100, 0x11FF],  # Hangul Jamo
  #[0x3000, 0x303F],  # CJK Symbols and Punctuation
  [0x3040, 0x309F],  # Hiragana
  [0x30A0, 0x30FF],  # Katakana
  [0x31F0, 0x31FF],  # Katakana Phonetic Extensions
  [0x3100, 0x312F],  # Bopomofo
  [0x31A0, 0x31BF],  # Bopomofo Extended (Bopomofo)
  [0x3130, 0x318F],  # Hangul Compatibility Jamo
  [0x3200, 0x32FF],  # Enclosed CJK Letters and Months
  [0x3300, 0x33FF],  # CJK Compatibility
  [0xAC00, 0xD7AF],  # Hangul Syllables
  [0x4E00, 0x9FFF],  # CJK Unified Ideographs
  [0x2E80, 0x2EFF],  # CJK Radicals Supplement (CJK Unified Ideographs)
  [0x2F00, 0x2FDF],  # Kangxi Radicals (CJK Unified Ideographs)
  [0x2FF0, 0x2FFF],  # Ideographic Description Characters (CJK Unified Ideographs)
  [0x3400, 0x4DBF],  # CJK Unified Ideographs Extension A (CJK Unified Ideographs)
  [0x20000, 0x2A6DF],  # CJK Unified Ideographs Extension B (CJK Unified Ideographs)
  [0x3190, 0x319F],  # Kanbun (CJK Unified Ideographs)
  [0x31C0, 0x31EF],  # CJK Strokes
  [0xF900, 0xFAFF],  # CJK Compatibility Ideographs (CJK Strokes)
  [0x2F800, 0x2FA1F],  # CJK Compatibility Ideographs Supplement (CJK Strokes)
  [0xA000, 0xA48F],  # Yi Syllables
  [0xA490, 0xA4CF],  # Yi Radicals
]
