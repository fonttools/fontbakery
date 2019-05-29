import pytest
from fontbakery.parse import _style_parse, instance_parse


def test_name():
    style = _style_parse("Bold Condensed")
    assert style.name == "Condensed Bold"

    style = _style_parse("Italic Bold Condensed")
    assert style.name == "Condensed Bold Italic"

    style = _style_parse("Extra-Bold")
    assert style.name == "ExtraBold"

    style = _style_parse("Extra Bold")
    assert style.name == "ExtraBold"

    style = _style_parse("Extra Bold Italic")
    assert style.name == "ExtraBold Italic"

    style = _style_parse("Semi Condensed Extra Light")
    assert style.name == "SemiCondensed ExtraLight"

    style = _style_parse("wt400 It")
    assert style.name == "Italic"

    style = _style_parse("Regular Italic")
    assert style.name == "Italic"

    style = _style_parse("ExLt ExCd It")
    assert style.name == "ExtraCondensed ExtraLight Italic"

    style = _style_parse("Thn It")
    assert style.name == "Thin Italic"

    style = _style_parse("Bold Oblique")
    assert style.name == "Bold Italic"

    style = _style_parse("UltCndExtBdIt")
    assert style.name =="UltraCondensed ExtraBold Italic"


def test_fvar_coordinates():
    style = instance_parse("Condensed Regular")
    assert style.coordinates == {"wght": 400.0, 'wdth': 75.0}

    style = instance_parse("UltraCondensed Black Italic")
    assert style.coordinates == {"wght": 900.0, 'wdth': 50.0}

