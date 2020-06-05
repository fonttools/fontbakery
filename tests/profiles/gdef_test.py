from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (WARN, PASS, SKIP)


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
  """ Are some spacing glyphs in GDEF mark glyph class? """
  from fontbakery.profiles.gdef import com_google_fonts_check_gdef_spacing_marks as check

  print ("Test: SKIP if a font lacks a GDEF table")
  test_font = get_test_font()
  status, message = list(check(test_font))[-1]
  assert status == SKIP

  print ("Test: PASS with an empty GDEF table")
  add_gdef_table(test_font, {})
  status, message = list(check(test_font))[-1]
  assert status == PASS

  print ("Test: WARN if a mark glyph has non-zero width")
  # Add a table with 'A' defined as a mark glyph:
  add_gdef_table(test_font, {'A': 3})
  status, message = list(check(test_font))[-1]
  assert status == WARN and message.code == 'spacing-mark-glyphs'


def test_check_gdef_mark_chars():
  """ Are some mark characters not in in GDEF mark glyph class? """
  from fontbakery.profiles.gdef import com_google_fonts_check_gdef_mark_chars as check

  print ("Test: SKIP if a font lacks a GDEF table...")
  test_font = get_test_font()
  status, message = list(check(test_font))[-1]
  assert status == SKIP

  print ("Test: WARN if a mark-char is not listed...")
  # Add a GDEF table not including `acutecomb` (U+0301) as a mark char:
  add_gdef_table(test_font, {})
  status, msg = list(check(test_font))[-1]
  assert status == WARN and msg.code == "mark-chars"
  assert 'U+0301' in msg.message

  print ("Test: PASS when properly declared...")
  # Include it in the table to see the check PASS:
  add_gdef_table(test_font, {'acutecomb': 3})
  status, message = list(check(test_font))[-1]
  assert status == PASS


def test_check_gdef_non_mark_chars():
  """ Are some non-mark characters in GDEF mark glyph class spacing? """
  from fontbakery.profiles.gdef import com_google_fonts_check_gdef_non_mark_chars as check

  print ("Test: SKIP if a font lacks a GDEF table...")
  test_font = get_test_font()
  status, message = list(check(test_font))[-1]
  assert status == SKIP

  print ("Test: PASS with an empty GDEF table")
  add_gdef_table(test_font, {})
  status, message = list(check(test_font))[-1]
  assert status == PASS

  print ("Test: PASS with an GDEF with only properly declared mark chars")
  add_gdef_table(test_font, {'acutecomb': 3})
  status, message = list(check(test_font))[-1]
  assert status == PASS

  print ("Test: PASS with an GDEF with a non-mark char (U+00B4, 'acute') misdeclared")
  add_gdef_table(test_font, {'acute': 3, 'acutecomb': 3})
  status, msg = list(check(test_font))[-1]
  assert status == WARN and msg.code == "non-mark-chars"
  assert 'U+00B4' in msg.message
