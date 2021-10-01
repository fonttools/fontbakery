import os

import defcon
import pytest

from fontbakery.checkrunner import (DEBUG, ERROR, FAIL, INFO, PASS, SKIP, WARN)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester)
from fontbakery.profiles.ufo_sources import profile as ufo_sources_profile

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)


@pytest.fixture
def empty_ufo_font(tmpdir):
    ufo = defcon.Font()
    ufo_path = str(tmpdir.join("empty_font.ufo"))
    ufo.save(ufo_path)
    return (ufo, ufo_path)


def test_check_ufolint(empty_ufo_font):
    check = CheckTester(ufo_sources_profile,
                        "com.daltonmaag/check/ufolint")

    _, ufo_path = empty_ufo_font

    assert_PASS(check(ufo_path),
                'with an empty UFO.')

    os.remove(os.path.join(ufo_path, "metainfo.plist"))
    assert_results_contain(check(ufo_path),
                           FAIL, "ufolint-fail",
                           'with maimed UFO.')


def test_check_required_fields(empty_ufo_font):
    check = CheckTester(ufo_sources_profile,
                        "com.daltonmaag/check/ufo-required-fields")

    ufo, _ = empty_ufo_font

    assert_results_contain(check(ufo),
                           FAIL, "missing-required-fields",
                           'with an empty UFO.')

    ufo.info.unitsPerEm = 1000
    ufo.info.ascender = 800
    ufo.info.descender = -200
    ufo.info.xHeight = 500
    ufo.info.capHeight = 700
    ufo.info.familyName = "Test"

    assert_PASS(check(ufo),
                'with an almost empty UFO.')


def test_check_recommended_fields(empty_ufo_font):
    check = CheckTester(ufo_sources_profile,
                        "com.daltonmaag/check/ufo-recommended-fields")

    ufo, _ = empty_ufo_font

    assert_results_contain(check(ufo),
                           WARN, "missing-recommended-fields",
                           'with an empty UFO.')

    ufo.info.postscriptUnderlineThickness = 1000
    ufo.info.postscriptUnderlinePosition = 800
    ufo.info.versionMajor = -200
    ufo.info.versionMinor = 500
    ufo.info.styleName = "700"
    ufo.info.copyright = "Test"
    ufo.info.openTypeOS2Panose = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert_PASS(check(ufo),
                'with an almost empty UFO.')


def test_check_unnecessary_fields(empty_ufo_font):
    check = CheckTester(ufo_sources_profile,
                        "com.daltonmaag/check/ufo-unnecessary-fields")

    ufo, _ = empty_ufo_font

    assert_PASS(check(ufo),
                'with an empty UFO.')

    ufo.info.openTypeNameUniqueID = "aaa"
    ufo.info.openTypeNameVersion = "1.000"
    ufo.info.postscriptUniqueID = -1
    ufo.info.year = 2018

    assert_results_contain(check(ufo),
                           WARN, "unnecessary-fields",
                           'with unnecessary fields in UFO.')

