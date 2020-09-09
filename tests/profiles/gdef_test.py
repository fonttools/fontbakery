from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables

from fontbakery.checkrunner import WARN
from fontbakery.codetesting import (assert_PASS,
                                    assert_SKIP,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


def get_test_font():
    import defcon
    import ufo2ft
    test_ufo = defcon.Font(TEST_FILE("test.ufo"))
    glyph = test_ufo.newGlyph("acute")
    glyph.unicode = 0x00B4
    glyph = test_ufo.newGlyph("acutecomb")
    glyph.unicode = 0x0301
    test_ttf = ufo2ft.compileTTF(test_ufo)

    # Make the CheckTester class happy... :-P
    test_ttf.reader.file.name = "in-memory-data.ttf"
    return test_ttf


def add_gdef_table(font, class_defs):
    font["GDEF"] = gdef = newTable("GDEF")
    class_def_table = otTables.GlyphClassDef()
    class_def_table.classDefs = class_defs
    gdef.table = otTables.GDEF()
    gdef.table.GlyphClassDef = class_def_table


def test_check_gdef_spacing_marks():
    """ Are some spacing glyphs in GDEF mark glyph class? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/gdef_spacing_marks")

    ttFont = get_test_font()
    assert_SKIP(check(ttFont),
                'if a font lacks a GDEF table...')

    add_gdef_table(ttFont, {})
    assert_PASS(check(ttFont),
                'with an empty GDEF table...')

    # Add a table with 'A' defined as a mark glyph:
    add_gdef_table(ttFont, {'A': 3})
    assert_results_contain(check(ttFont),
                           WARN, 'spacing-mark-glyphs',
                           'if a mark glyph has non-zero width...')


def test_check_gdef_mark_chars():
    """ Are some mark characters not in in GDEF mark glyph class? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/gdef_mark_chars")

    ttFont = get_test_font()
    assert_SKIP(check(ttFont),
                'if a font lacks a GDEF table...')

    # Add a GDEF table not including `acutecomb` (U+0301) as a mark char:
    add_gdef_table(ttFont, {})
    message = assert_results_contain(check(ttFont),
                                     WARN, 'mark-chars',
                                     'if a mark-char is not listed...')
    assert 'U+0301' in message

    # Include it in the table to see the check PASS:
    add_gdef_table(ttFont, {'acutecomb': 3})
    assert_PASS(check(ttFont),
                'when properly declared...')


def test_check_gdef_non_mark_chars():
    """ Are some non-mark characters in GDEF mark glyph class spacing? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/gdef_non_mark_chars")

    ttFont = get_test_font()
    assert_SKIP(check(ttFont),
                'if a font lacks a GDEF table...')

    add_gdef_table(ttFont, {})
    assert_PASS(check(ttFont),
                'with an empty GDEF table.')

    add_gdef_table(ttFont, {'acutecomb': 3})
    assert_PASS(check(ttFont),
                'with an GDEF with only properly declared mark chars.')

    add_gdef_table(ttFont, {'acute': 3, 'acutecomb': 3})
    message = assert_results_contain(check(ttFont),
                                     WARN, 'non-mark-chars',
                                     'with an GDEF with a non-mark char (U+00B4, "acute") misdeclared')
    assert 'U+00B4' in message

