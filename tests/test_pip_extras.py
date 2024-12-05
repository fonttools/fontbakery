import sys
from unittest.mock import patch

import pytest
from fontTools.ttLib import TTFont

from conftest import ImportRaiser, remove_import_raiser
from fontbakery.codetesting import CheckTester, TEST_FILE


def test_lxml_etree_extra_needed_exit(monkeypatch):
    module_name = "lxml.etree"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)
    from fontbakery.checks.fontvalidator import check_fontvalidator

    with pytest.raises(SystemExit):
        list(check_fontvalidator(None, None))

    remove_import_raiser(module_name)


def test_google_protobuf_extra_needed_exit_from_conditions(monkeypatch):
    check = CheckTester("googlefonts/metadata/designer_profiles")
    module_name = "google.protobuf"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    with pytest.raises(SystemExit):
        font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
        check(font)

    remove_import_raiser(module_name)


def test_axisregistry_extra_needed_exit(monkeypatch):
    check = CheckTester("googlefonts/canonical_filename")
    module_name = "axisregistry"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    with pytest.raises(SystemExit):
        ttFont = TTFont(TEST_FILE("cabinvfbeta/Cabin-VF.ttf"))
        check(ttFont)

    remove_import_raiser(module_name)


def test_uharfbuzz_extra_needed_exit(monkeypatch):
    module_name = "uharfbuzz"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)
    from fontbakery.checks.iso15008.utils import pair_kerning

    with pytest.raises(SystemExit):
        pair_kerning(None, None, None)

    remove_import_raiser(module_name)


@patch("vharfbuzz.Vharfbuzz", side_effect=ImportError)
def test_extra_needed_exit(mock_import_error):
    check = CheckTester("shaping/regression")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    with patch("sys.exit") as mock_exit:
        check(font)
        mock_exit.assert_called()
