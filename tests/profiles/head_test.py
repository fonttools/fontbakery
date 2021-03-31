import io
import os

import pytest
from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (WARN, FAIL)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


mada_fonts = [
    TEST_FILE("mada/Mada-Black.ttf"),
    TEST_FILE("mada/Mada-ExtraLight.ttf"),
    TEST_FILE("mada/Mada-Medium.ttf"),
    TEST_FILE("mada/Mada-SemiBold.ttf"),
    TEST_FILE("mada/Mada-Bold.ttf"),
    TEST_FILE("mada/Mada-Light.ttf"),
    TEST_FILE("mada/Mada-Regular.ttf")
]

@pytest.fixture
def mada_ttFonts():
    return [TTFont(path) for path in mada_fonts]


def test_check_family_equal_font_versions(mada_ttFonts):
    """ Make sure all font files have the same version value. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/family/equal_font_versions")

    # our reference Mada family is know to be good here.
    assert_PASS(check(mada_ttFonts),
                'with good family.')

    bad_ttFonts = mada_ttFonts
    # introduce a mismatching version value into the second font file:
    version = bad_ttFonts[0]['head'].fontRevision
    bad_ttFonts[1]['head'].fontRevision = version + 1

    assert_results_contain(check(bad_ttFonts),
                           WARN, 'mismatch',
                           'with fonts that diverge on the fontRevision field value.')


def test_check_unitsperem():
    """ Checking unitsPerEm value is reasonable. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/unitsperem")

    # In this test we'll forge several known-good and known-bad values.
    # We'll use Mada Regular to start with:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    for good_value in [16, 32, 64, 128, 256, 512, 1000,
                       1024, 2000, 2048, 4096, 8192, 16384]:
        ttFont['head'].unitsPerEm = good_value
        assert_PASS(check(ttFont),
                    f'with a good value of unitsPerEm = {good_value} ...')

    for warn_value in [20, 50, 100, 500, 4000]:
        ttFont['head'].unitsPerEm = warn_value
        assert_results_contain(check(ttFont),
                               WARN, 'suboptimal',
                               f'with a value of unitsPerEm = {warn_value} ...')

    # These are arbitrarily chosen bad values:
    for bad_value in [0, 1, 2, 4, 8, 10, 15, 16385, 32768]:
        ttFont['head'].unitsPerEm = bad_value
        assert_results_contain(check(ttFont),
                               FAIL, 'out-of-range',
                               f'with a bad value of unitsPerEm = {bad_value} ...')


def test_parse_version_string():
    """ Checking font version fields. """
    from fontbakery.profiles.head import parse_version_string
    import fractions

    version_tests_good = {
        "Version 01.234": fractions.Fraction("1.234"),
        "1.234": fractions.Fraction("1.234"),
        "01.234; afjidfkdf 5.678": fractions.Fraction("1.234"),
        "1.3": fractions.Fraction("1.300"),
        "1.003": fractions.Fraction("1.003"),
        "1.0": fractions.Fraction(1),
        "1.000": fractions.Fraction(1),
        "3.000;NeWT;Nunito-Regular": fractions.Fraction("3"),
        "Something Regular Italic Version 1.234": fractions.Fraction("1.234")
    }

    version_tests_bad = ["Version 0x.234",
                         "x",
                         "212122;asdf 01.234"]

    for string, version in version_tests_good.items():
        assert parse_version_string(string) == version

    for string in version_tests_bad:
        with pytest.raises(ValueError):
            parse_version_string(string)


def test_check_font_version():
    """ Checking font version fields. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/font_version")

    test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")
    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    # 1.00099 is only a mis-interpretation of a valid float value (1.001)
    # See more detailed discussion at:
    # https://github.com/googlefonts/fontbakery/issues/2006
    test_font = TTFont(test_font_path)
    test_font["head"].fontRevision = 1.00098
    test_font["name"].setName("Version 1.001", 5, 1, 0, 0x0)
    test_font["name"].setName("Version 1.001", 5, 3, 1, 0x409)

    # There should be at least one WARN...
    assert_results_contain(check(test_font),
                           WARN, "near-mismatch")

    # But final result is a PASS:
    assert_PASS(check(test_font))

    # Test that having more than 3 decimal places in the version
    # in the Name table is acceptable.
    # See https://github.com/googlefonts/fontbakery/issues/2928
    test_font = TTFont(test_font_path)
    # This is the nearest multiple of 1/65536 to 2020.0613
    test_font["head"].fontRevision = 2020.061294555664
    test_font["name"].setName("Version 2020.0613", 5, 1, 0, 0x0)
    test_font["name"].setName("Version 2020.0613", 5, 3, 1, 0x409)
    assert_PASS(check(test_font))

    test_font = TTFont(test_font_path)
    test_font["head"].fontRevision = 3.1
    test_font["name"].setName("Version 3.000", 5, 1, 0, 0x0)
    test_font["name"].setName("Version 3.000", 5, 3, 1, 0x409)
    assert_results_contain(check(test_font),
                           FAIL, 'mismatch')

    test_font = TTFont(test_font_path)
    test_font["head"].fontRevision = 3.0
    test_font["name"].setName("Version 1.000", 5, 3, 1, 0x409)
    assert_results_contain(check(test_font),
                           FAIL, 'mismatch')

    test_font = TTFont(test_font_path)
    test_font["name"].setName("Version x.000", 5, 3, 1, 0x409)
    assert_results_contain(check(test_font),
                           FAIL, 'parse')

    test_font = TTFont(test_font_path)
    v1 = test_font["name"].getName(5, 3, 1)
    v2 = test_font["name"].getName(5, 1, 0)
    test_font["name"].names.remove(v1)
    test_font["name"].names.remove(v2)
    assert_results_contain(check(test_font),
                           FAIL, 'missing')

