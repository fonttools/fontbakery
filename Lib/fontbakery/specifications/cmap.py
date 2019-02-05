from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import


@check(
  id = 'com.google.fonts/check/013'
)
def com_google_fonts_check_013(ttFonts):
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
    yield FAIL, "Fonts have different unicode encodings."
  else:
    yield PASS, "Fonts have equal unicode encodings."


# This check was originally ported from
# Mekkablue Preflight Checks available at:
# https://github.com/mekkablue/Glyphs-Scripts/blob/master/Test/Preflight%20Font.py
@check(
  id = 'com.google.fonts/check/077',
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/735'
  }
)
def com_google_fonts_check_077(ttFont):
  """Check all glyphs have codepoints assigned."""
  failed = False
  for subtable in ttFont['cmap'].tables:
    if subtable.isUnicode():
      for item in subtable.cmap.items():
        codepoint = item[0]
        if codepoint is None:
          failed = True
          yield FAIL, ("Glyph {} lacks a unicode"
                       " codepoint assignment").format(codepoint)
  if not failed:
    yield PASS, "All glyphs have a codepoint value assigned."
