from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import


@check(
  id = 'com.google.fonts/check/family/equal_unicode_encodings'
)
def com_google_fonts_check_family_equal_unicode_encodings(ttFonts):
  """Fonts have equal unicode encodings?"""
  encoding = None
  failed = False
  for ttFont in ttFonts:
    cmap = None
    for table in ttFont['cmap'].tables:
      if table.format == 4:
        cmap = table
        break
    # Could a font lack a format 4 cmap table ?
    # If we ever find one of those, it would crash the check here.
    # Then we'd have to yield a FAIL regarding the missing table entry.
    if not encoding:
      encoding = cmap.platEncID
    if encoding != cmap.platEncID:
      failed = True
  if failed:
    yield FAIL,\
          Message("mismatch",
                  "Fonts have different unicode encodings.")
  else:
    yield PASS, "Fonts have equal unicode encodings."


# This check was originally ported from
# Mekkablue Preflight Checks available at:
# https://github.com/mekkablue/Glyphs-Scripts/blob/master/Test/Preflight%20Font.py
@check(
  id = 'com.google.fonts/check/all_glyphs_have_codepoints',
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/735'
  }
)
def com_google_fonts_check_all_glyphs_have_codepoints(ttFont):
  """Check all glyphs have codepoints assigned."""
  failed = False
  for subtable in ttFont['cmap'].tables:
    if subtable.isUnicode():
      for item in subtable.cmap.items():
        codepoint = item[0]
        if codepoint is None:
          failed = True
          yield FAIL,\
                Message("glyph-lacks-codepoint",
                        f"Glyph {codepoint} lacks a unicode"
                        f" codepoint assignment.")
  if not failed:
    yield PASS, "All glyphs have a codepoint value assigned."
