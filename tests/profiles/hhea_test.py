import os

from fontbakery.utils import TEST_FILE
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

def test_check_linegaps():
  """ Checking Vertical Metric Linegaps. """
  from fontbakery.profiles.hhea import com_google_fonts_check_linegaps as check

  print('Test FAIL with non-zero hhea.lineGap...')
  # Our reference Mada Regular is know to be bad here.
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

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


def test_check_maxadvancewidth():
  """ MaxAdvanceWidth is consistent with values in the Hmtx and Hhea tables? """
  from fontbakery.profiles.hhea import com_google_fonts_check_maxadvancewidth as check

  test_font = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))

  status, _ = list(check(test_font))[-1]
  assert status == PASS

  test_font["hmtx"].metrics["A"] = (1234567, 1234567)
  status, _ = list(check(test_font))[-1]
  assert status == FAIL


def test_check_monospace_max_advancewidth():
  """ Monospace font has hhea.advanceWidthMax equal
      to each glyph's advanceWidth? """
  from fontbakery.profiles.hhea import com_google_fonts_check_monospace_max_advancewidth as check
  from fontbakery.profiles.shared_conditions import glyph_metrics_stats

  test_font_path = TEST_FILE("cousine/Cousine-Regular.ttf")

  test_font = TTFont(test_font_path)
  import fontTools.subset
  subsetter = fontTools.subset.Subsetter()
  subsetter.populate(glyphs="A")  # Arbitrarily remove everything except n.
  subsetter.subset(test_font)
  stats = glyph_metrics_stats(test_font)
  status, _ = list(check(test_font, stats))[-1]
  assert status == PASS

  metrics_A = test_font["hmtx"].metrics["A"]
  test_font["hmtx"].metrics["A"] = (metrics_A[0] + 1, metrics_A[1])
  stats = glyph_metrics_stats(test_font)
  status, message = list(check(test_font, stats))[-1]
  assert status == WARN
  assert message.code == "should-be-monospaced"

  test_font["hmtx"].metrics["A"] = (metrics_A[0] + metrics_A[0], metrics_A[1])
  stats = glyph_metrics_stats(test_font)
  status, message = list(check(test_font, stats))[-1]
  assert status == WARN
  assert message.code == "variable-monospaced"

  test_font["hmtx"].metrics["A"] = (0, metrics_A[1])
  stats = glyph_metrics_stats(test_font)
  status, message = list(check(test_font, stats))[-1]
  assert status == WARN
  assert message.code == "variable-monospaced"
