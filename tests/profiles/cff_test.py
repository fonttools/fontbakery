from fontTools.ttLib import TTFont

from fontbakery.utils import (TEST_FILE,
                              assert_PASS,
                              assert_results_contain)
from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL)

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_cff_call_depth():
    from fontbakery.profiles.cff import com_adobe_fonts_check_cff_call_depth \
        as check

    # this font's CFF subr call depths should all be <= 10:
    test_font_path = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    # in this font, glyphs D & E exceed max call depth,
    # and glyph F calls a subroutine that calls itself
    test_font_path = TEST_FILE(
        'subr_test_fonts/subr_test_font_infinite_recursion.otf')
    test_font = TTFont(test_font_path)

    assert_results_contain(check(test_font),
                           FAIL, 'max-depth',
                           '- Subroutine call depth exceeded'
                           ' maximum of 10 for glyph "D".')

    assert_results_contain(check(test_font),
                           FAIL, 'max-depth',
                           '- Subroutine call depth exceeded'
                           ' maximum of 10 for glyph "E".')

    assert_results_contain(check(test_font),
                           FAIL, 'recursion-error',
                           '- Recursion error while decompiling glyph "F".')


def test_check_cff2_call_depth():
    from fontbakery.profiles.cff import com_adobe_fonts_check_cff2_call_depth \
        as check
    # this font's CFF subr call depths should all be <= 10:
    test_font_path = TEST_FILE(
        'source-sans-pro/VAR/SourceSansVariable-Roman.otf')
    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    # in this font, glyphs D & E exceed max call depth,
    # and glyph F calls a subroutine that calls itself
    test_font_path = TEST_FILE(
        'subr_test_fonts/var_subr_test_font_infinite_recursion.otf')
    test_font = TTFont(test_font_path)

    assert_results_contain(check(test_font),
                           FAIL, 'max-depth',
                           'Subroutine call depth exceeded'
                           ' maximum of 10 for glyph "D".')

    assert_results_contain(check(test_font),
                           FAIL, 'max-depth',
                           'Subroutine call depth exceeded'
                           ' maximum of 10 for glyph "E".')

    assert_results_contain(check(test_font),
                           FAIL, 'recursion-error',
                           'Recursion error while decompiling glyph "F".')
