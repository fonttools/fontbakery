from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (WARN, PASS)


def get_test_font():
  import defcon
  import ufo2ft
  test_ufo = defcon.Font(TEST_FILE("test.ufo"))
  glyph = test_ufo.newGlyph("acute")
  glyph.unicode = 0x00B4
  glyph = test_ufo.newGlyph("acutecomb")
  glyph.unicode = 0x0301
  test_ttf = ufo2ft.compileTTF(test_ufo)
  return test_ttf


def add_gdef_table(font, class_defs):
  font["GDEF"] = gdef = newTable("GDEF")
  class_def_table = otTables.GlyphClassDef()
  class_def_table.classDefs = class_defs
  gdef.table = otTables.GDEF()
  gdef.table.GlyphClassDef = class_def_table


def test_check_gdef_spacing_marks():
  """Are some spacing glyphs in GDEF mark glyph class? """
  from fontbakery.profiles.gdef import com_google_fonts_check_gdef_spacing_marks as check

  test_font = get_test_font()
  status, message = list(check(test_font))[-1]
  assert status == PASS
  assert message == 'Font does not declare an optional "GDEF" table or has '\
      'any GDEF glyph class definition.'

  add_gdef_table(test_font, {})
  status, message = list(check(test_font))[-1]
  assert status == PASS
  assert message == 'Font does not has spacing glyphs in the GDEF mark glyph class.'

  add_gdef_table(test_font, {'A': 3})
  status, message = list(check(test_font))[-1]
  msg = ": ".join(msg.strip() for msg in str(message).split(":"))
  assert (status, msg) == (
    WARN,
    'The following spacing glyphs may be in the GDEF mark glyph class by '\
    'mistake: A [code: spacing-mark-glyphs]'
  )


def test_check_gdef_mark_chars():
  """Are some mark characters not in in GDEF mark glyph class? """
  from fontbakery.profiles.gdef import com_google_fonts_check_gdef_mark_chars as check

  test_font = get_test_font()
  status, message = list(check(test_font))[-1]
  assert status == PASS
  assert message == 'Font does not declare an optional "GDEF" table or has '\
      'any GDEF glyph class definition.'

  add_gdef_table(test_font, {})
  status, message = list(check(test_font))[-1]
  assert status == WARN
  msg = str(message)
  assert msg.split(":")[0], msg.split(":")[1].strip() == (
    'The following mark characters could be in the GDEF mark glyph class',
    'U+0301'
  )

  add_gdef_table(test_font, {'acutecomb': 3})
  status, message = list(check(test_font))[-1]
  assert status, message == (
    PASS,
    'Font does not have mark characters not in '\
    'the GDEF mark glyph class.'
  )

def test_check_gdef_non_mark_chars():
  """Are some non-mark characters in GDEF mark glyph class spacing? """
  from fontbakery.profiles.gdef import com_google_fonts_check_gdef_non_mark_chars as check

  test_font = get_test_font()
  status, message = list(check(test_font))[-1]
  assert status == PASS
  assert message == 'Font does not declare an optional "GDEF" table or has '\
      'any GDEF glyph class definition.'

  add_gdef_table(test_font, {})
  status, message = list(check(test_font))[-1]
  assert status == PASS
  assert message == 'Font does not have non-mark characters in '\
    'the GDEF mark glyph class.'

  add_gdef_table(test_font, {'acutecomb': 3})
  status, message = list(check(test_font))[-1]
  assert status == PASS
  assert message == 'Font does not have non-mark characters in '\
    'the GDEF mark glyph class.'

  add_gdef_table(test_font, {'acute': 3, 'acutecomb': 3})
  status, message = list(check(test_font))[-1]
  assert status == WARN and message.code == "non-mark-chars"
  msg = str(message)
  assert msg.split(":")[0], msg.split(":")[1].strip() == (
    'The following non-mark characters should not be in '\
    'the GDEF mark glyph class:\n',
    'U+00B4'
  )
