from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('ligature_glyphs', ))
]

@check(
  id = 'com.google.fonts/check/ligature_carets',
  conditions = ['ligature_glyphs'],
  rationale = """
    All ligatures in a font must have corresponding caret (text cursor)
    positions defined in the GDEF table, otherwhise, users may experience
    issues with caret rendering.
  """,
  misc_metadata = {
    'request': 'https://github.com/googlefonts/fontbakery/issues/1225'
  }
)
def com_google_fonts_check_ligature_carets(ttFont, ligature_glyphs):
  """Are there caret positions declared for every ligature?"""
  if ligature_glyphs == -1:
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
    lig_caret_list = ttFont["GDEF"].table.LigCaretList
    if lig_caret_list is None:
      missing = set(ligature_glyphs)
    else:
      missing = set(ligature_glyphs) - set(lig_caret_list.Coverage.glyphs)

    if lig_caret_list is None or lig_caret_list.LigGlyphCount == 0:
      yield WARN, Message("lacks-caret-pos",
                          ("This font lacks caret position values for"
                           " ligature glyphs on its GDEF table."))
    elif missing:
      missing = "\n\t- ".join(missing)
      yield WARN, Message("incomplete-caret-pos-data",
                          ("This font lacks caret positioning"
                           " values for these ligature glyphs:"
                           f"\n\t- {missing}\n\n  "))
    else:
      yield PASS, "Looks good!"
