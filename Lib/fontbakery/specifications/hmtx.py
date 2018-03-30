from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA

from .shared_conditions import missing_whitespace_chars
# flake8 F401, F811:
(missing_whitespace_chars, )

@check(
    id='com.google.fonts/check/050',
    conditions=['not missing_whitespace_chars'])
def com_google_fonts_check_050(ttFont):
  """Whitespace glyphs have coherent widths?"""
  from fontbakery.utils import getGlyph

  def getGlyphWidth(font, glyph):
    return font['hmtx'][glyph][0]

  space = getGlyph(ttFont, 0x0020)
  nbsp = getGlyph(ttFont, 0x00A0)

  spaceWidth = getGlyphWidth(ttFont, space)
  nbspWidth = getGlyphWidth(ttFont, nbsp)

  if spaceWidth != nbspWidth or nbspWidth < 0:
    if nbspWidth > spaceWidth and spaceWidth >= 0:
      yield FAIL, Message("bad_space", ("space {} nbsp {}: Space advanceWidth"
                                        " needs to be fixed"
                                        " to {}.").format(
                                            spaceWidth, nbspWidth, nbspWidth))
    else:
      yield FAIL, Message("bad_nbsp", ("space {} nbsp {}: Nbsp advanceWidth"
                                       " needs to be fixed "
                                       "to {}").format(spaceWidth, nbspWidth,
                                                       spaceWidth))
  else:
    yield PASS, "Whitespace glyphs have coherent widths."
