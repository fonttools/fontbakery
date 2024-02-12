from fontbakery.status import WARN, SKIP
from fontbakery.codetesting import (
    assert_results_contain,
    CheckTester,
    TEST_FILE,
    assert_PASS,
)


def test_check_outline_alignment_miss():
    """Check for misaligned points."""
    check = CheckTester("com.google.fonts/check/outline_alignment_miss")

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-misalignments")
    messages = "".join([m.message.message for m in results])
    assert "A (U+0041): X=3.0,Y=-2.0 (should be at baseline 0?)" in messages

    # TODO: PASS


def test_check_outline_short_segments():
    """Check for short segments."""
    check = CheckTester("com.google.fonts/check/outline_short_segments")

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-short-segments")
    messages = "".join([m.message.message for m in results])
    assert (
        "D (U+0044) contains a short segment L<<180.0,68.0>--<173.0,71.0>>" in messages
    )

    # TODO: PASS

    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg


def test_check_outline_colinear_vectors():
    """Check for colinear line segments."""
    check = CheckTester("com.google.fonts/check/outline_colinear_vectors")

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-colinear-vectors")
    messages = "".join([m.message.message for m in results])
    assert "A (U+0041)" not in messages
    assert "B (U+0042)" not in messages
    assert "C (U+0043)" in messages
    assert "E (U+0045)" in messages
    assert ".notdef" not in messages

    # TODO: PASS

    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg


def test_check_outline_jaggy_segments():
    """Check for jaggy segments."""
    check = CheckTester("com.google.fonts/check/outline_jaggy_segments")

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-jaggy-segments")
    messages = "".join([m.message.message for m in results])
    assert "* E (U+0045)" in messages

    filename = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(filename))

    filename = TEST_FILE("source-sans-pro/OTF/SourceSansPro-LightItalic.otf")
    assert_PASS(check(filename))

    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg


def test_check_outline_semi_vertical():
    """Check for semi-vertical/semi-horizontal lines."""
    check = CheckTester("com.google.fonts/check/outline_semi_vertical")

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-semi-vertical")
    messages = "".join([m.message.message for m in results])
    assert "* B (U+0042)" in messages
    assert "* E (U+0045)" not in messages

    # TODO: PASS

    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg

    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Italic.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_italic" in msg
