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

# from fontTools.ttLib import TTFont

def NOT_IMPLEMENTED_test_check_072():
  """ Font enables smart dropout control in "prep" table instructions? """
  # from fontbakery.specifications.general import com_google_fonts_check_072 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - SKIP, "Not applicable to a CFF font."
  # - PASS, "Program at 'prep' table contains instructions enabling smart dropout control."
  # - WARN, "Font does not contain TrueType instructions enabling
  #          smart dropout control in the 'prep' table program."
