from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
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
  id = 'com.google.fonts/check/gpos_kerning_info'
)
def com_google_fonts_check_gpos_kerning_info(ttFont):
  """Does GPOS table have kerning information?"""
  if not has_kerning_info(ttFont):
    yield WARN, "GPOS table lacks kerning information."
  else:
    yield PASS, "GPOS table has got kerning information."


@check(
  id = 'com.google.fonts/check/kerning_for_non_ligated_sequences',
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
def com_google_fonts_check_kerning_for_non_ligated_sequences(ttFont, ligatures, has_kerning_info):
  """Is there kerning info for non-ligated sequences?"""

  def look_for_nonligated_kern_info(table):
    for pairpos in table.SubTable:
      for i, glyph in enumerate(pairpos.Coverage.glyphs):
        if not hasattr(pairpos, 'PairSet'):
          continue
        for pairvalue in pairpos.PairSet[i].PairValueRecord:
          kern_pair = (glyph, pairvalue.SecondGlyph)
          if kern_pair in ligature_pairs:
            ligature_pairs.remove(kern_pair)

  def ligatures_str(pairs):
    result = [f"\t- {first} + {second}" for first, second in pairs]
    return "\n".join(result)

  if ligatures == -1:
    yield FAIL, Message("malformed", "Failed to lookup ligatures."
                        " This font file seems to be malformed."
                        " For more info, read:"
                        " https://github.com"
                        "/googlefonts/fontbakery/issues/1596")
  else:
    ligature_pairs = []
    for first, comp in ligatures.items():
      for components in comp:
        while components:
          pair = (first, components[0])
          if pair not in ligature_pairs:
            ligature_pairs.append(pair)
          first = components[0]
          components.pop(0)

    for record in ttFont["GSUB"].table.FeatureList.FeatureRecord:
      if record.FeatureTag == 'kern':
        for index in record.Feature.LookupListIndex:
          lookup = ttFont["GSUB"].table.LookupList.Lookup[index]
          look_for_nonligated_kern_info(lookup)

    if ligature_pairs:
      yield WARN, Message("lacks-kern-info",
                          ("GPOS table lacks kerning info for the following"
                           " non-ligated sequences:\n"
                           "{}\n\n  ").format(ligatures_str(ligature_pairs)))
    else:
      yield PASS, ("GPOS table provides kerning info for "
                   "all non-ligated sequences.")
