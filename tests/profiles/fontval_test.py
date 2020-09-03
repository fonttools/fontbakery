import os
import pytest

from fontbakery.codetesting import (TEST_FILE,
                                    assert_results_contain)
from fontbakery.checkrunner import ERROR
from fontbakery.profiles import fontval as fontval_profile


def test_check_fontvalidator():
    """ MS Font Validator checks """
    from fontbakery.profiles.fontval import com_google_fonts_check_fontvalidator as check

    font = TEST_FILE("mada/Mada-Regular.ttf")

    # Then we make sure that there wasn't an ERROR
    # which would mean FontValidator is not properly installed:
    for status, message in check(font):
        assert status != ERROR

    # Simulate FontVal missing.
    old_path = os.environ["PATH"]
    os.environ["PATH"] = ""
    with pytest.raises(OSError) as _:
        assert_results_contain(check(font),
                               ERROR, None) # FIXME: This needs a message keyword!
    os.environ["PATH"] = old_path

