import io

from fontTools.ttLib import TTFont

from fontbakery.checkrunner import WARN
from fontbakery.codetesting import (assert_results_contain,
                                    CheckTester,
                                    TEST_FILE,
                                    assert_PASS)
from fontbakery.profiles import path as path_profile


def test_check_path_alignment_miss():
    """ Check for misaligned points. """
    check = CheckTester(path_profile,
                        "com.google.fonts/check/path_alignment_miss")

    ttFont = TTFont(TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf"))
    results = check(ttFont)
    assert_results_contain(results,
                           WARN, 'found-misalignments')
    messages = "".join([m[1].message for m in results])
    assert "A: X=3.0,Y=-2.0 (should be at baseline 0?)" in messages

def test_check_path_colinear_vectors():
    """ Check for colinear line segments. """
    check = CheckTester(path_profile,
                        "com.google.fonts/check/path_colinear_vectors")

    ttFont = TTFont(TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf"))
    results = check(ttFont)
    assert_results_contain(results,
                           WARN, 'found-colinear-vectors')
    messages = "".join([m[1].message for m in results])
    assert "* A" not in messages
    assert "* B" not in messages
    assert "* C" in messages

def test_check_path_jaggy_segments():
    """ Check for jaggy segments. """
    check = CheckTester(path_profile,
                        "com.google.fonts/check/path_jaggy_segments")

    ttFont = TTFont(TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf"))
    results = check(ttFont)
    assert_results_contain(results,
                           WARN, 'found-jaggy-segments')
    messages = "".join([m[1].message for m in results])
    assert "* E" in messages

    ttFont = TTFont(TEST_FILE("familysans/FamilySans-Regular.ttf"))
    assert_PASS(check(ttFont))


def test_check_path_semi_vertical():
    """ Check for semi-vertical/semi-horizontal lines. """
    check = CheckTester(path_profile,
                        "com.google.fonts/check/path_semi_vertical")

    ttFont = TTFont(TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf"))
    results = check(ttFont)
    assert_results_contain(results,
                           WARN, 'found-semi-vertical')
    messages = "".join([m[1].message for m in results])
    assert "* B" in messages
    assert "* E" not in messages
