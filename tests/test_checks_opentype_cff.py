from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    TEST_FILE,
)
from fontbakery.status import DEBUG, INFO, WARN, ERROR, SKIP, PASS, FAIL

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


@check_id("opentype/cff_call_depth")
def test_check_cff_call_depth(check):
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
        '- Subroutine call depth exceeded maximum of 10 for glyph "D".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "max-depth",
        '- Subroutine call depth exceeded maximum of 10 for glyph "E".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "recursion-error",
        '- Recursion error while decompiling glyph "F".',
    )


@check_id("opentype/cff2_call_depth")
def test_check_cff2_call_depth(check):
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
        'Subroutine call depth exceeded maximum of 10 for glyph "D".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "max-depth",
        'Subroutine call depth exceeded maximum of 10 for glyph "E".',
    )

    assert_results_contain(
        check(font),
        FAIL,
        "recursion-error",
        'Recursion error while decompiling glyph "F".',
    )


@check_id("opentype/cff_deprecated_operators")
def test_check_cff_deprecated_operators(check):
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
        (
            'Glyph "Agrave" has deprecated use of "endchar" operator'
            " to build accented characters (seac)."
        ),
    )


@check_id("opentype/cff_ascii_strings")
def test_check_cff_strings(check):
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))

    # check that a healthy CFF font passes:
    assert_PASS(check(ttFont))

    # FIXME: The condition cff_analysis creates a new ttFont object
    #        and, consequently, discards the modifications we made
    #        here prior to invoking the check.
    #
    # # put an out of range char into FullName field:
    # rawDict = ttFont["CFF "].cff.topDictIndex[0].rawDict
    # rawDict["FullName"] = "S\u00F2urceSansPro-Regular"
    # assert_results_contain(
    #     check(ttFont),
    #     FAIL,
    #     "cff-string-not-in-ascii-range",
    #     (
    #         "The following CFF TopDict strings are not in the ASCII range:"
    #         f"- FullName: {rawDict['FullName']}"
    #     ),
    # )

    # Out-of-ascii-range char in the FontName field will cause decode issues:
    ttFont = TTFont(TEST_FILE("unicode-decode-err/unicode-decode-err-cff.otf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "cff-unable-to-decode",
        (
            "Unable to decode CFF table, possibly due to out "
            "of ASCII range strings. Please check table strings."
        ),
    )
