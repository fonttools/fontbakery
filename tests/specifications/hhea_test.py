# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_041():
  """ Checking Vertical Metric Linegaps. """
  from fontbakery.specifications.hhea import com_google_fonts_check_041 as check

  print('Test FAIL with non-zero hhea.lineGap...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont("data/test/mada/Mada-Regular.ttf")

  # But just to be sure, we first explicitely set
  # the values we're checking for:
  ttFont['hhea'].lineGap = 1
  ttFont['OS/2'].sTypoLineGap = 0
  status, message = list(check(ttFont))[-1]
  assert status == WARN and message.code == "hhea"

  # Then we run the check with a non-zero OS/2.sTypoLineGap:
  ttFont['hhea'].lineGap = 0
  ttFont['OS/2'].sTypoLineGap = 1
  status, message = list(check(ttFont))[-1]
  assert status == WARN and message.code == "OS/2"

  # And finaly we fix it by making both values equal to zero:
  ttFont['hhea'].lineGap = 0
  ttFont['OS/2'].sTypoLineGap = 0
  status, message = list(check(ttFont))[-1]
  assert status == PASS


def NOT_IMPLEMENTED_test_check_073():
  """ MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_073 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, "Failed to find advance width data in HMTX table!"
  # - FAIL, "AdvanceWidthMax mismatch"
  # - PASS


def NOT_IMPLEMENTED_test_check_079():
  """ Monospace font has hhea.advanceWidthMax equal
      to each glyph's advanceWidth? """
  # from fontbakery.specifications.googlefonts import com_google_fonts_check_079 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - WARN, "This seems to be a monospaced font."
  # - WARN, "Double-width and/or zero-width glyphs were detected."
  # - PASS
