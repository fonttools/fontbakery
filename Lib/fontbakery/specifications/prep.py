from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import PASS, WARN
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

@check(
  id = 'com.google.fonts/check/072',
  conditions = ['is_ttf']
)
def com_google_fonts_check_072(ttFont):
  """Font enables smart dropout control in "prep" table instructions?

  B8 01 FF    PUSHW 0x01FF
  85          SCANCTRL (unconditinally turn on
                        dropout control mode)
  B0 04       PUSHB 0x04
  8D          SCANTYPE (enable smart dropout control)

  Smart dropout control means activating rules 1, 2 and 5:
  Rule 1: If a pixel's center falls within the glyph outline,
          that pixel is turned on.
  Rule 2: If a contour falls exactly on a pixel's center,
          that pixel is turned on.
  Rule 5: If a scan line between two adjacent pixel centers
          (either vertical or horizontal) is intersected
          by both an on-Transition contour and an off-Transition
          contour and neither of the pixels was already turned on
          by rules 1 and 2, turn on the pixel which is closer to
          the midpoint between the on-Transition contour and
          off-Transition contour. This is "Smart" dropout control.
  """
  INSTRUCTIONS = b"\xb8\x01\xff\x85\xb0\x04\x8d"

  if ("prep" in ttFont and
      INSTRUCTIONS in ttFont["prep"].program.getBytecode()):
    yield PASS, ("Program at 'prep' table contains instructions"
                  " enabling smart dropout control.")
  else:
    yield WARN, ("Font does not contain TrueType instructions enabling"
                  " smart dropout control in the 'prep' table program."
                  " Please try exporting the font with autohinting enabled.")
