from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import


def _is_non_mark_char(charcode):
  from fontTools import unicodedata
  category = unicodedata.category(chr(charcode))
  if category.startswith("C"):
    # skip control characters
    return None
  elif not category.startswith("M"):
    return True
  return False


def _get_mark_class_glyphs(ttFont):
  from fontbakery.constants import GDEF_MARK_GLYPH_CLASS
  class_defs = ttFont["GDEF"].table.GlyphClassDef.classDefs.items()
  return {name for (name, value) in class_defs
          if value == GDEF_MARK_GLYPH_CLASS}


@check(
  id = 'com.google.fonts/check/gdef_spacing_marks',
  rationale = """
    Glyphs in the GDEF mark glyph class should be non-spacing.
    Spacing glyphs in the GDEF mark glyph class may have incorrect
    anchor positioning that was only intended for building composite glyphs
    during design.
  """
)
def com_google_fonts_check_gdef_spacing_marks(ttFont):
  """Check mark characters are in GDEF mark glyph class)"""
  from fontbakery.utils import pretty_print_list

  if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
    spacing_glyphs = {name for (name, value) in ttFont["hmtx"].metrics.items()
                      if value}
    mark_class_glyphs = _get_mark_class_glyphs(ttFont)
    spacing_glyphs_in_mark_glyph_class = spacing_glyphs & mark_class_glyphs
    if spacing_glyphs_in_mark_glyph_class :
      formatted_list = "\t " +\
        pretty_print_list(sorted(spacing_glyphs_in_mark_glyph_class),
                          shorten=10,
                          sep=", ")
      yield WARN,\
            Message('spacing-mark-glyphs',
                    f"The following spacing glyphs may be in"
                    f" the GDEF mark glyph class by mistake:\n"
                    f"{formatted_list}")
    else:
      yield PASS, ('Font does not has spacing glyphs'
                   ' in the GDEF mark glyph class.')
  else:
    yield PASS, ('Font does not declare an optional "GDEF" table'
                 ' or has any GDEF glyph class definition.')


@check(
  id = 'com.google.fonts/check/gdef_mark_chars',
  rationale = """
    Mark characters should be in the GDEF mark glyph class.
  """,
)
def com_google_fonts_check_gdef_mark_chars(ttFont):
  """Check mark characters are in GDEF mark glyph class"""
  from fontbakery.utils import pretty_print_list

  if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
    cmap = ttFont.getBestCmap()
    mark_char_glyphs = {
      charcode for charcode in cmap
      if _is_non_mark_char(charcode) is False
    }
    mark_class_glyphs = _get_mark_class_glyphs(ttFont)
    mark_char_glyphs_not_in_mark_class = mark_char_glyphs - mark_class_glyphs
    if mark_char_glyphs_not_in_mark_class:
      formatted_marks = "\t " +\
        pretty_print_list(sorted("U+%04X" % c for c in
                                 mark_char_glyphs_not_in_mark_class),
                          shorten=None,
                          sep=", ")
      yield WARN,\
            Message('mark-chars',
                    f"The following mark characters could be"
                    f" in the GDEF mark glyph class:\n"
                    f"{formatted_marks}")
    else:
      yield PASS, ('Font does not have mark characters'
                   ' not in the GDEF mark glyph class.')
  else:
    yield PASS, ('Font does not declare an optional "GDEF" table'
                 ' or has any GDEF glyph class definition.')


@check(
  id = 'com.google.fonts/check/gdef_non_mark_chars',
  rationale = """
    Glyphs in the GDEF mark glyph class become non-spacing and may be
    repositioned if they have mark anchors. Only combining mark glyphs
    should be in that class. Any non-mark glyph must not be in that class,
    in particular spacing glyphs.
  """,
)
def com_google_fonts_check_gdef_non_mark_chars(ttFont):
  """Check GDEF mark glyph class doesn't have characters that are not marks)"""
  from fontbakery.utils import pretty_print_list

  if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
    cmap = ttFont.getBestCmap()
    nonmark_chars = {
      charcode for charcode in cmap
      if _is_non_mark_char(charcode) is True
    }
    nonmark_char_glyphs = {cmap[c] for c in nonmark_chars}
    glyph_to_char_mapping = dict()
    for k, v in cmap.items():
      if v in glyph_to_char_mapping:
        glyph_to_char_mapping[v].add(k)
      else:
        glyph_to_char_mapping[v] = {k}
    mark_class_glyphs = _get_mark_class_glyphs(ttFont)
    nonmark_char_glyphs_in_mark_class = nonmark_char_glyphs & mark_class_glyphs
    if nonmark_char_glyphs_in_mark_class:
      nonmark_chars_in_mark_class = set()
      for glyph in nonmark_char_glyphs_in_mark_class:
        chars = glyph_to_char_mapping[glyph]
        for char in chars:
          if char in nonmark_chars:
            nonmark_chars_in_mark_class.add(char)
      formatted_nonmarks = "\t " +\
        pretty_print_list(sorted("U+%04X" % c for c in
                                 nonmark_chars_in_mark_class),
                          shorten=None,
                          sep=", ")
      yield WARN,\
            Message('non-mark-chars',
                    f"The following non-mark characters should"
                    f" not be in the GDEF mark glyph class:\n"
                    f"{formatted_nonmarks}")
    else:
      yield PASS, ('Font does not have non-mark characters'
                   ' in the GDEF mark glyph class.')
  else:
    yield PASS, ('Font does not declare an optional "GDEF" table'
                 ' or has any GDEF glyph class definition.')
