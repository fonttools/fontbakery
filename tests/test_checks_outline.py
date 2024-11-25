from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.status import WARN, SKIP
from fontbakery.codetesting import (
    assert_results_contain,
    TEST_FILE,
    assert_PASS,
)


@check_id("outline_alignment_miss")
def test_check_outline_alignment_miss(check):
    """Check for misaligned points."""

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-misalignments")
    messages = "".join([m.message.message for m in results])
    assert "A (U+0041): X=3.0,Y=-2.0 (should be at baseline 0?)" in messages

    # TODO: PASS


@check_id("outline_alignment_miss")
def test_check_outline_alignment_os2_old(check):
    """Test that the outline_alignment_miss check works when
    the OS/2 table has a low version and does not have the
    xHeight and CapHeight fields that are normally used."""

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    assert ttFont["OS/2"].version == 3

    results = check(ttFont)
    assert not any([r.status == WARN for r in results])
    # Passes (but only because there are too many near misses)
    assert_PASS(check(ttFont))

    # Downgrade OS/2 version
    ttFont["OS/2"].version = 2

    results = check(ttFont)
    assert not any([r.status == WARN for r in results])
    # Passes (but only because there are too many near misses)
    assert_PASS(check(ttFont))

    # Downgrade OS/2 to version 1
    ttFont["OS/2"].version = 1
    del ttFont["OS/2"].sxHeight
    del ttFont["OS/2"].sCapHeight
    del ttFont["OS/2"].usDefaultChar
    del ttFont["OS/2"].usBreakChar
    del ttFont["OS/2"].usMaxContext

    assert_results_contain(check(ttFont), WARN, "skip-cap-x-height-alignment")


@check_id("outline_short_segments")
def test_check_outline_short_segments(check):
    """Check for short segments."""

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


@check_id("outline_colinear_vectors")
def test_check_outline_colinear_vectors(check):
    """Check for colinear line segments."""

    filename = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    results = check(filename)
    assert_results_contain(results, WARN, "found-colinear-vectors")
    messages = "".join([m.message.message for m in results])
    assert "A (U+0041)" not in messages
    assert "B (U+0042)" not in messages
    assert "C (U+0043)" in messages
    assert "E (U+0045)" in messages

    # TODO: PASS

    font = TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf")
    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not is_variable_font" in msg


@check_id("outline_jaggy_segments")
def test_check_outline_jaggy_segments(check):
    """Check for jaggy segments."""

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


@check_id("outline_semi_vertical")
def test_check_outline_semi_vertical(check):
    """Check for semi-vertical/semi-horizontal lines."""

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


@check_id("outline_direction")
def test_check_outline_direction(check):
    """Check for misaligned points."""

    font = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.otf")
    assert_results_contain(check(font), SKIP, "unfulfilled-conditions")

    font = TEST_FILE("wonky_paths/WonkySourceSansPro-Regular.ttf")
    results = check(font)
    assert_results_contain(results, WARN, "ccw-outer-contour")
    messages = "".join([m.message.message for m in results])
    assert "A (U+0041) has a counter-clockwise outer contour" in messages
    assert " x (U+0078) has a path with no bounds (probably a single point)" in messages

    font = TEST_FILE("wonky_paths/OutlineTest.ttf")
    assert_PASS(check(font))


@check_id("overlapping_path_segments")
def test_check_overlapping_path_segments(check):
    # Check a font that contains overlapping path segments
    filename = TEST_FILE("overlapping_path_segments/Figtree[wght].ttf")
    results = check(filename)
    assert_results_contain(results, WARN, "overlapping-path-segments")

    # check a font that doesn't contain overlapping path segments
    filename = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    results = check(filename)
    assert_PASS(results)
