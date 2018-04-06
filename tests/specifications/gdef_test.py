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

def test_check_064():
  """ Is there a caret position declared for every ligature ? """
  from fontbakery.specifications.gdef import com_google_fonts_check_064 as check
  from fontbakery.specifications.shared_conditions import ligatures

  # Our reference Mada Medium is known to be bad
  ttFont = TTFont("data/test/mada/Mada-Medium.ttf")
  lig = ligatures(ttFont)

  # So it must emit a WARN:
  print ("Test WARN with a bad font...")
  status, message = list(check(ttFont, lig))[-1]
  assert status == WARN and message.code == "lacks-caret-pos"

  # And FamilySans Regular is known to be bad
  ttFont = TTFont("data/test/familysans/FamilySans-Regular.ttf")
  lig = ligatures(ttFont)

  # So it must emit a WARN:
  print ("Test WARN with a bad font...")
  status, message = list(check(ttFont, lig))[-1]
  assert status == WARN and message.code == "GDEF-missing"

  # TODO: test the following code-paths:
  # - WARN "incomplete-caret-pos-data"
  # - FAIL "malformed"
  # - PASS (We currently lack a reference family that PASSes this check!)
