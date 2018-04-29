from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

spec_imports = [
    ('.shared_conditions', ('ligatures', ))
]


@condition
def has_kerning_info(ttFont):
  """A font has kerning info if it has a GPOS table containing at least one
  Pair Adjustment lookup (eigther directly or through an extension
  subtable)."""
  if "GPOS" not in ttFont:
    return False

  if not ttFont["GPOS"].table.LookupList:
    return False

  for lookup in ttFont["GPOS"].table.LookupList.Lookup:
    if lookup.LookupType == 2:  # type 2 = Pair Adjustment
      return True
    elif lookup.LookupType == 9:  # type 9 = Extension subtable
      for ext in lookup.SubTable:
        if ext.ExtensionLookupType == 2:  # type 2 = Pair Adjustment
          return True


@check(
  id = 'com.google.fonts/check/063'
)
def com_google_fonts_check_063(ttFont):
  """Does GPOS table have kerning information?"""
  if not has_kerning_info(ttFont):
    yield WARN, "GPOS table lacks kerning information."
  else:
    yield PASS, "GPOS table has got kerning information."


@check(
  id = 'com.google.fonts/check/065',
  rationale = """
    Fonts with ligatures should have kerning on the corresponding
    non-ligated sequences for text where ligatures aren't used
    (eg https://github.com/impallari/Raleway/issues/14).
  """,
  conditions = ['ligatures',
                'has_kerning_info'],
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1145'
  })
def com_google_fonts_check_065(ttFont, ligatures, has_kerning_info):
  """Is there kerning info for non-ligated sequences?"""
  remaining = ligatures

  def look_for_nonligated_kern_info(table):
    for pairpos in table.SubTable:
      for i, glyph in enumerate(pairpos.Coverage.glyphs):
        if glyph in ligatures.keys():
          if not hasattr(pairpos, 'PairSet'):
            continue
          for pairvalue in pairpos.PairSet[i].PairValueRecord:
            if (glyph in ligatures and glyph in remaining and
                pairvalue.SecondGlyph in ligatures[glyph]):
              del remaining[glyph]

  def ligatures_str(ligs):
    result = []
    for first in ligs:
      result.extend(["{}_{}".format(first, second) for second in ligs[first]])
    return result

  if ligatures == -1:
    yield FAIL, Message("malformed", "Failed to lookup ligatures."
                        " This font file seems to be malformed."
                        " For more info, read:"
                        " https://github.com"
                        "/googlefonts/fontbakery/issues/1596")
  else:
    for lookup in ttFont["GPOS"].table.LookupList.Lookup:
      if lookup.LookupType == 2:  # type 2 = Pair Adjustment
        look_for_nonligated_kern_info(lookup)
      # elif lookup.LookupType == 9:
      #   if lookup.SubTable[0].ExtensionLookupType == 2:
      #     look_for_nonligated_kern_info(lookup.SubTable[0])

    if remaining != {}:
      yield WARN, Message("lacks-kern-info",
                          ("GPOS table lacks kerning info for the following"
                           " non-ligated sequences: "
                           "{}").format(ligatures_str(remaining)))
    else:
      yield PASS, ("GPOS table provides kerning info for "
                   "all non-ligated sequences.")
