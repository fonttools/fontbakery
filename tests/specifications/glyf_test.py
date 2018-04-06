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

def NOT_IMPLEMENTED_test_check_069():
  """ Is there any unused data at the end of the glyf table? """
  # from fontbakery.specifications.general import com_google_fonts_check_069 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - SKIP, "This check does not support CFF fonts."
  # - FAIL, code="unreachable-data"
  # - FAIL, code="data-beyond-table-end"
  # - PASS, "There is no unused data at the end of the glyf table."


def NOT_IMPLEMENTED_test_check_075():
  """ Check for points out of bounds. """
  # from fontbakery.specifications.general import com_google_fonts_check_075 as check
  # TODO: Implement-me!
  #
  # code-paths:
  # - WARN, "Some glyphs have out of bounds coordinates."
  # - PASS, "All glyph paths have coordinates within bounds!"
