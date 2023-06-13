import pytest
import shutil

from fontbakery.codetesting import TEST_FILE, assert_results_contain
from fontbakery.checkrunner import ERROR
from fontbakery.profiles import fontval as fontval_profile


@pytest.mark.skipif(
    not shutil.which("FontValidator"),
    reason="FontValidator is not installed on your system",
)
def test_check_fontvalidator():
    """MS Font Validator checks"""
    # check = CheckTester(fontval_profile,
    #                     "com.google.fonts/check/fontvalidator")
    check = fontval_profile.com_google_fonts_check_fontvalidator

    font = TEST_FILE("mada/Mada-Regular.ttf")
    config = {}

    # Then we make sure that there wasn't an ERROR
    # which would mean FontValidator is not properly installed:
    for status, message in check(font, config):
        assert status != ERROR

    # Simulate FontVal missing.
    import os

    old_path = os.environ["PATH"]
    os.environ["PATH"] = ""
    with pytest.raises(OSError) as _:
        assert_results_contain(check(font, config), ERROR, "fontval-not-available")
    os.environ["PATH"] = old_path
