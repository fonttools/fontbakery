from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import INFO, PASS


@check(
    id='com.google.fonts/check/066',
    request="https://github.com/googlefonts/fontbakery/issues/1675",
    rationale="""
      Even though, all fonts should have their kerning implemented
      in the GPOS table, there may be kerning info at the kern table as well.

      Some applications such as MS PowerPoint require kerning info on
      the kern table. More specifically, they require a format 0 kern
      subtable from a kern table version 0, which is the only one that
      Windows understands (and which is also the simplest and more limited
      of all the kern subtables).

      Google Fonts ingests fonts made for download and use as desktops, and
      does all web font optimizations in the serving pipeline (using libre
      libraries that anyone can replicate.)

      Ideally, TTFs intended for desktop users (and thus the ones intended
      for Google Fonts) should have both KERN and GPOS tables.

      Given all of the above, we currently treat kerning on a v0 kern table
      as a good-to-have (but optional) feature.
  """)
def com_google_fonts_check_066(ttFont):
  """Is there a "kern" table declared in the font?"""

  if "kern" in ttFont:
    yield INFO, ("Only a few programs may require the kerning"
                 " info that this font provides on its \"kern\" table.")
    # TODO: perhaps we should add code here to detect and emit an ERROR
    #       if the kern table and subtable version and format are not zero,
    #       as mentioned in the rationale above.
  else:
    yield PASS, "Font does not declare an optional \"kern\" table."
