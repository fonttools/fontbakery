# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import os

from fontTools.ttLib import TTFont
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



def test_check_075():
  """ Check for points out of bounds. """
  from fontbakery.specifications.glyf import com_google_fonts_check_075 as check

  test_font = TTFont(
      os.path.join("data", "test", "nunito", "Nunito-Regular.ttf"))
  status, _ = list(check(test_font))[-1]
  assert status == WARN

  test_font2 = TTFont(
      os.path.join("data", "test", "familysans", "FamilySans-Regular.ttf"))
  status, _ = list(check(test_font2))[-1]
  assert status == PASS
