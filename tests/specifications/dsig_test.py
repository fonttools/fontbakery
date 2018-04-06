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

def test_check_045():
  """ Does the font have a DSIG table ? """
  from fontbakery.specifications.dsig import com_google_fonts_check_045 as check

  # Our reference Cabin Regular font is good (theres a DSIG table declared):
  ttFont = TTFont("data/test/cabin/Cabin-Regular.ttf")

  # So it must PASS the check:
  print ("Test PASS with a good font...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # Then we remove the DSIG table so that we get a FAIL:
  print ("Test FAIL with a font lacking a DSIG table...")
  del ttFont['DSIG']
  status, message = list(check(ttFont))[-1]
  assert status == FAIL
