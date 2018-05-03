# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

import os

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

def test_check_072():
  """ Font enables smart dropout control in "prep" table instructions? """
  # TODO: Implement-me!
  #
  # code-paths:
  # - SKIP, "Not applicable to a CFF font."
  # - PASS, "Program at 'prep' table contains instructions enabling smart dropout control."
  # - WARN, "Font does not contain TrueType instructions enabling
  #          smart dropout control in the 'prep' table program."
  from fontbakery.specifications.prep import com_google_fonts_check_072 as check

  test_font_path = os.path.join("data", "test", "nunito", "Nunito-Regular.ttf")

  test_font = TTFont(test_font_path)
  status, _ = list(check(test_font))[-1]
  assert status == PASS

  import array
  test_font["prep"].program.bytecode = array.array('B', [0])
  status, _ = list(check(test_font))[-1]
  assert status == WARN
