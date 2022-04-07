from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)
from fontbakery.checkrunner import DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL
from fontbakery.profiles import cff as cff_profile

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


def test_check_cff_call_depth():
    check = CheckTester(cff_profile, "com.adobe.fonts/check/cff_call_depth")

    # this font's CFF subr call depths should all be <= 10:
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    assert_PASS(check(font))

    # in this font, glyphs D & E exceed max call depth,
    # and glyph F calls a subroutine that calls itself
    font = TEST_FILE("subr_test_fonts/subr_test_font_infinite_recursion.otf")

    assert_results_contain(
        check(font),
        FAIL,
        "max-depth",
        "- Subroutine call depth exceeded" ' maximum of 10 for glyph "D".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "max-depth",
        "- Subroutine call depth exceeded" ' maximum of 10 for glyph "E".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "recursion-error",
        '- Recursion error while decompiling glyph "F".',
    )


def test_check_cff2_call_depth():
    check = CheckTester(cff_profile, "com.adobe.fonts/check/cff2_call_depth")

    # this font's CFF subr call depths should all be <= 10:
    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    assert_PASS(check(font))

    # in this font, glyphs D & E exceed max call depth,
    # and glyph F calls a subroutine that calls itself
    font = TEST_FILE("subr_test_fonts/var_subr_test_font_infinite_recursion.otf")

    assert_results_contain(
        check(font),
        FAIL,
        "max-depth",
        "Subroutine call depth exceeded" ' maximum of 10 for glyph "D".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "max-depth",
        "Subroutine call depth exceeded" ' maximum of 10 for glyph "E".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "recursion-error",
        'Recursion error while decompiling glyph "F".',
    )


def test_check_cff_deprecated_operators():
    check = CheckTester(cff_profile, "com.adobe.fonts/check/cff_deprecated_operators")

    # this font uses the deprecated 'dotsection' operator
    font = TEST_FILE("deprecated_operators/cff1_dotsection.otf")
    assert_results_contain(
        check(font),
        WARN,
        "deprecated-operator-dotsection",
        'Glyph "i" uses deprecated "dotsection" operator.',
    )

    # this font uses the 'endchar' operator in a manner that is deprecated ("seac")
    font = TEST_FILE("deprecated_operators/cff1_endchar_seac.otf")
    assert_results_contain(
        check(font),
        FAIL,
        "deprecated-operation-endchar-seac",
        'Glyph "Agrave" has deprecated use of "endchar" operator to build accented characters (seac).',
    )
