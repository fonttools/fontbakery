from fontbakery.callable import check, condition
from fontbakery.checkrunner import PASS, WARN
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import


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
  id = 'com.google.fonts/check/gpos_kerning_info'
)
def com_google_fonts_check_gpos_kerning_info(ttFont):
  """Does GPOS table have kerning information?"""
  if not has_kerning_info(ttFont):
    yield WARN,\
          Message("lacks-kern-info",
                  "GPOS table lacks kerning information.")
  else:
    yield PASS, "GPOS table has got kerning information."
