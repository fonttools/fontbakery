import shutil

import pytest

from conftest import check_id
from fontbakery.codetesting import TEST_FILE, assert_results_contain
from fontbakery.status import ERROR


@pytest.mark.skipif(
    not shutil.which("FontValidator"),
    reason="FontValidator is not installed on your system",
)
@check_id("fontvalidator")
def test_check_fontvalidator(check):
    """MS Font Validator checks"""

    font = TEST_FILE("mada/Mada-Regular.ttf")

    # Then we make sure that there wasn't an ERROR
    # which would mean FontValidator is not properly installed:
    for subresult in check(font):
        assert subresult.status != ERROR

    # Simulate FontVal missing.
    import os

    old_path = os.environ["PATH"]
    os.environ["PATH"] = ""
    with pytest.raises(OSError) as _:
        assert_results_contain(check(font), ERROR, "fontval-not-available")
    os.environ["PATH"] = old_path
