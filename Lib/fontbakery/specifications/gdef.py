from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = [
    ('.shared_conditions', ('ligatures', ))
]

@check(
  id = 'com.google.fonts/check/064',
  conditions = ['ligatures'],
  rationale = """
    All ligatures in a font must have corresponding caret (text cursor)
    positions defined in the GDEF table, otherwhise, users may experience
    issues with caret rendering.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1225'
  }
)
def com_google_fonts_check_064(ttFont, ligatures):
  """Is there a caret position declared for every ligature?"""
  if ligatures == -1:
    yield FAIL, Message("malformed", "Failed to lookup ligatures."
                        " This font file seems to be malformed."
                        " For more info, read:"
                        " https://github.com"
                        "/googlefonts/fontbakery/issues/1596")
  elif "GDEF" not in ttFont:
    yield WARN, Message("GDEF-missing",
                        ("GDEF table is missing, but it is mandatory"
                         " to declare it on fonts that provide ligature"
                         " glyphs because the caret (text cursor)"
                         " positioning for each ligature must be"
                         " provided in this table."))
  else:
    # TODO: After getting a sample of a good font,
    #       resume the implementation of this routine:
    lig_caret_list = ttFont["GDEF"].table.LigCaretList
    if lig_caret_list is None or lig_caret_list.LigGlyphCount == 0:
      yield WARN, Message("lacks-caret-pos",
                          ("This font lacks caret position values for"
                           " ligature glyphs on its GDEF table."))
    elif lig_caret_list.LigGlyphCount != len(ligatures):
      yield WARN, Message("incomplete-caret-pos-data",
                          ("It seems that this font lacks caret positioning"
                           " values for some of its ligature glyphs on the"
                           " GDEF table. There's a total of {} ligatures,"
                           " but only {} sets of caret positioning"
                           " values.").format(
                               len(ligatures), lig_caret_list.LigGlyphCount))
    else:
      # Should we also actually check each individual entry here?
      yield PASS, "Looks good!"
