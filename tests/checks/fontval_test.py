import shutil
import sys

import pytest

from conftest import ImportRaiser, remove_import_raiser

from fontbakery.codetesting import TEST_FILE, assert_results_contain, CheckTester
from fontbakery.status import ERROR


def test_extra_needed_exit(monkeypatch):
    module_name = "lxml.etree"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)
    from fontbakery.checks.fontval import com_google_fonts_check_fontvalidator

    with pytest.raises(SystemExit):
        list(com_google_fonts_check_fontvalidator(None, None))

    remove_import_raiser(module_name)


@pytest.mark.skipif(
    not shutil.which("FontValidator"),
    reason="FontValidator is not installed on your system",
)
def test_check_fontvalidator():
    """MS Font Validator checks"""
    check = CheckTester("com.google.fonts/check/fontvalidator")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    config = {}

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
