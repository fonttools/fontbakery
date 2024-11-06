from fontbakery.status import FAIL
from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    TEST_FILE,
)

def test_check_family_single_directory():
    """Fonts are all in the same directory."""
    check = CheckTester("family/single_directory")
    same_dir = [
        TEST_FILE("cabin/Cabin-Thin.ttf"),
        TEST_FILE("cabin/Cabin-ExtraLight.ttf"),
    ]
    multiple_dirs = [
        TEST_FILE("mada/Mada-Regular.ttf"),
        TEST_FILE("cabin/Cabin-ExtraLight.ttf"),
    ]

    assert_PASS(check(same_dir), f"with same dir: {same_dir}")

    assert_results_contain(
        check(multiple_dirs),
        FAIL,
        "single-directory",
        f"with multiple dirs: {multiple_dirs}",
    )
