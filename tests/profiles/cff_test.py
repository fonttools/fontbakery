from fontTools.ttLib import TTFont

from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_cff_call_depth():
    from fontbakery.profiles.cff import com_adobe_fonts_check_cff_call_depth \
        as check

    # this font's CFF subr call depths should all be <= 10:
    test_font_path = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    test_font = TTFont(test_font_path)
    status, message = list(check(test_font))[-1]
    assert status == PASS

    # in this font, glyphs D & E exceed max call depth,
    # and glyph F calls a subroutine that calls itself
    test_font_path = TEST_FILE(
        'subr_test_fonts/subr_test_font_infinite_recursion.otf')
    test_font = TTFont(test_font_path)
    results = list(check(test_font))

    EXPECTED_RESULTS = [
        (FAIL, "max-depth", 'Subroutine call depth exceeded maximum of 10 for glyph "D".'),
        (FAIL, "max-depth", 'Subroutine call depth exceeded maximum of 10 for glyph "E".'),
        (FAIL, "recursion-error", 'Recursion error while decompiling glyph "F".')]

    for status, msg in results:
      assert (status, msg.code, msg.message) in EXPECTED_RESULTS


def test_check_cff2_call_depth():
    from fontbakery.profiles.cff import com_adobe_fonts_check_cff2_call_depth \
        as check
    # this font's CFF subr call depths should all be <= 10:
    test_font_path = TEST_FILE(
        'source-sans-pro/VAR/SourceSansVariable-Roman.otf')
    test_font = TTFont(test_font_path)
    status, message = list(check(test_font))[-1]
    assert status == PASS

    # in this font, glyphs D & E exceed max call depth,
    # and glyph F calls a subroutine that calls itself
    test_font_path = TEST_FILE(
        'subr_test_fonts/var_subr_test_font_infinite_recursion.otf')
    test_font = TTFont(test_font_path)
    results = list(check(test_font))

    EXPECTED_RESULTS = [
        (FAIL, "max-depth", 'Subroutine call depth exceeded maximum of 10 for glyph "D".'),
        (FAIL, "max-depth", 'Subroutine call depth exceeded maximum of 10 for glyph "E".'),
        (FAIL, "recursion-error", 'Recursion error while decompiling glyph "F".')]

    for status, msg in results:
      assert (status, msg.code, msg.message) in EXPECTED_RESULTS
