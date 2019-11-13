import os

from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.checkrunner import Section, WARN, PASS #, INFO, ERROR, SKIP, FAIL
from fontbakery.callable import check #, disable
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory
from fontbakery.constants import (PlatformID,
                                  WindowsEncodingID,
                                  UnicodeEncodingID,
                                  MacintoshEncodingID)


from .googlefonts_conditions import * # pylint: disable=wildcard-import,unused-wildcard-import
profile_imports = ('fontbakery.profiles.universal',) # Maybe this should be .googlefonts instead...
profile = profile_factory(default_section=Section("Noto Fonts"))

CMAP_TABLE_CHECKS = [
  'com.google.fonts/check/cmap/unexpected_subtables',
]

OS2_TABLE_CHECKS = [
  'com.google.fonts/check/unicode_range_bits',
]

# Maybe this should be GOOGLEFONTS_PROFILE_CHECKS instead...
NOTOFONTS_PROFILE_CHECKS = \
  UNIVERSAL_PROFILE_CHECKS + \
  CMAP_TABLE_CHECKS + \
  OS2_TABLE_CHECKS


@check(
  id = 'com.google.fonts/check/cmap/unexpected_subtables',
  rationale = """
    There are just a few typical types of cmap subtables that are used in fonts.
    If anything different is declared in a font, it will be treated as a FAIL.
  """
)
def com_google_fonts_check_cmap_unexpected_subtables(ttFont):
  """Ensure all cmap subtables are the typical types expected in a font."""
  from fontbakery.profiles.shared_conditions import is_cjk_font

  passed = True
  # Note:
  #   Format 0 = Byte encoding table
  #   Format 4 = Segment mapping to delta values 
  #   Format 6 = Trimmed table mapping
  #   Format 12 = Segmented coverage
  #   Format 14 = Unicode Variation Sequences
  EXPECTED_SUBTABLES = [
    ( 0, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),     # 13.7% of GFonts TTFs (389 files)
    #( 4, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),     # only the Sansation family has this on GFonts
    ( 6, PlatformID.MACINTOSH, MacintoshEncodingID.ROMAN),     # 38.1% of GFtons TTFs (1.082 files)
    #( 4, PlatformID.UNICODE,   UnicodeEncodingID.UNICODE_1_0), # only the Gentium family has this on GFonts
    #(12, PlatformID.UNICODE, 10), # INVALID? - only the Overpass family and SawarabiGothic-Regular has this on GFonts
    # -----------------------------------------------------------------------
    ( 4, PlatformID.WINDOWS, WindowsEncodingID.UNICODE_BMP),                 # Absolutely all GFonts TTFs have this table :-)
    (12, PlatformID.WINDOWS, WindowsEncodingID.UNICODE_FULL_REPERTOIRE),     #   5.7% of GFonts TTFs (162 files)
    (14, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_VARIATION_SEQUENCES), #   1.1% - Only 4 families (30 TTFs),
                                                                             #          including SourceCodePro, have this on GFonts
    ( 4, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_2_0_BMP_ONLY),        #  97.0% of GFonts TTFs (only 84 files lack it)
    (12, PlatformID.UNICODE, UnicodeEncodingID.UNICODE_2_0_FULL)             #   2.9% of GFonts TTFs (82 files)
  ]
  if is_cjk_font(ttFont):
    EXPECTED_SUBTABLES.extend([
      # Adobe says historically some programs used these to identify
      # the script in the font.  The encodingID is the quickdraw
      # script manager code.  These are dummy tables.
      (6, PlatformID.MACINTOSH, MacintoshEncodingID.JAPANESE),
      (6, PlatformID.MACINTOSH, MacintoshEncodingID.CHINESE_TRADITIONAL),
      (6, PlatformID.MACINTOSH, MacintoshEncodingID.KOREAN),
      (6, PlatformID.MACINTOSH, MacintoshEncodingID.CHINESE_SIMPLIFIED)
    ])

  for subtable in ttFont['cmap'].tables:
    if (subtable.format,
        subtable.platformID,
        subtable.platEncID) not in EXPECTED_SUBTABLES:
      passed = False
      yield WARN,\
            Message("unexpected-subtable",
                    f"'cmap' has a subtable of"
                    f" (format={subtable.format}, platform={subtable.platformID},"
                    f" encoding={subtable.platEncID}), which it shouldn't have.")
  if passed:
    yield PASS, "All cmap subtables look good!"


@check(
  id = 'com.google.fonts/check/unicode_range_bits',
  rationale = """
    When the UnicodeRange bits on the OS/2 table are not properly set, some programs running on Windows may not recognize the font and use a system fallback font instead. For that reason, this check calculates the proper settings by inspecting the glyphs declared on the cmap table and then ensures that their corresponding ranges are enabled.
  """,
  conditions = ["unicoderange",
                "preferred_cmap"]
)
def com_google_fonts_check_unicode_range_bits(ttFont, unicoderange, preferred_cmap):
  """Ensure UnicodeRange bits are properly set."""
  from fontbakery.constants import UNICODERANGE_DATA
  from fontbakery.utils import (compute_unicoderange_bits,
                                unicoderange_bit_name,
                                chars_in_range)
  expected_unicoderange = compute_unicoderange_bits(ttFont)
  difference = unicoderange ^ expected_unicoderange
  if not difference:
    yield PASS, "Looks good!"
  else:
    for bit in range(128):
      if difference & (1 << bit):
        range_name = unicoderange_bit_name(bit)
        num_chars = len(chars_in_range(ttFont, bit))
        range_size = sum(entry[3] - entry[2] + 1 for entry in UNICODERANGE_DATA[bit])
        set_unset = "1"
        if num_chars == 0:
          set_unset = "0"
          num_chars = "none"
        yield WARN, \
              Message("bad-range-bit",
                      f'UnicodeRange bit {bit} "{range_name}" should be {set_unset} because'
                      f' cmap has {num_chars} of the {range_size} codepoints in this range.')

profile.auto_register(globals())
profile.test_expected_checks(NOTOFONTS_PROFILE_CHECKS, exclusive=True)
