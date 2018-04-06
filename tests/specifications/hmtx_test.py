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

# the original check itself has unclear semantics, so that needs to be reviewed first
def NOT_IMPLEMENTED_test_check_050():
  """ Whitespace glyphs have coherent widths? """
  # from fontbakery.specifications.hmtx import com_google_fonts_check_050 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - FAIL, code="bad_space"
  # - FAIL, code="bad_nbsp"
  # - PASS
