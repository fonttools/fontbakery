import shutil
import sys

import pytest

from conftest import ImportRaiser, remove_import_raiser, reload_module

from fontbakery.codetesting import TEST_FILE, assert_results_contain
from fontbakery.status import ERROR
from fontbakery.profiles import fontval as fontval_profile


def test_extra_needed_exit(monkeypatch):
    module_name = "lxml.etree"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    with pytest.raises(SystemExit):
        reload_module("fontbakery.profiles.fontval")

    remove_import_raiser(module_name)


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
