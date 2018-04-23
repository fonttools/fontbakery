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


def NOT_IMPLEMENTED_test_check_069():
  """ Is there any unused data at the end of the glyf table? """
  # from fontbakery.specifications.general import com_google_fonts_check_069 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, code="unreachable-data"
  # - FAIL, code="data-beyond-table-end"
  # - PASS, "There is no unused data at the end of the glyf table."


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
