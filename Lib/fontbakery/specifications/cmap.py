from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS


@check(id='com.google.fonts/check/013')
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


@check(id='com.google.fonts/check/076')
def com_google_fonts_check_076(ttFont):
  """Check glyphs have unique unicode codepoints."""
  failed = False
  for subtable in ttFont['cmap'].tables:
    if subtable.isUnicode():
      codepoints = {}
      for codepoint, name in subtable.cmap.items():
        codepoints.setdefault(codepoint, set()).add(name)
      for value in codepoints.keys():
        if len(codepoints[value]) >= 2:
          failed = True
          yield FAIL, ("These glyphs carry the same"
                       " unicode value {}:"
                       " {}").format(value, ", ".join(codepoints[value]))
  if not failed:
    yield PASS, "All glyphs have unique unicode codepoint assignments."


@check(id='com.google.fonts/check/077')
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


@check(id='com.google.fonts/check/078')
def com_google_fonts_check_078(ttFont):
  """Check that glyph names do not exceed max length."""
  failed = False
  for subtable in ttFont['cmap'].tables:
    for item in subtable.cmap.items():
      name = item[1]
      if len(name) > 109:
        failed = True
        yield FAIL, ("Glyph name is too long:" " '{}'").format(name)
  if not failed:
    yield PASS, "No glyph names exceed max allowed length."
