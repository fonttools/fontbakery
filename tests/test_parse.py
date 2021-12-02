import pytest
from fontbakery.parse import _style_parse, instance_parse


def test_name():
    style = _style_parse("Extra-Bold")
    assert style.name == "ExtraBold"

    style = _style_parse("Extra Bold")
    assert style.name == "ExtraBold"

    style = _style_parse("Extra Bold Italic")
    assert style.name == "ExtraBold Italic"

    style = _style_parse("wt400 It")
    assert style.name == "Italic"

    style = _style_parse("Regular Italic")
    assert style.name == "Italic"

    style = _style_parse("Thn It")
    assert style.name == "Thin Italic"

    style = _style_parse("Bold Oblique")
    assert style.name == "Bold Italic"


def test_fvar_coordinates():
    style = instance_parse("Regular")
    assert style.coordinates == {"wght": 400.0}

    style = instance_parse("Black Italic")
    assert style.coordinates == {"wght": 900.0}

    style = instance_parse("Regular")
    assert style.coordinates == {"wght": 400.0}

    style = instance_parse("Italic")
    assert style.coordinates == {"wght": 400.0}


def test_unparsable_tokens():
    # https://github.com/googlefonts/fontbakery/issues/2701#issuecomment-585870359
    style = instance_parse("144 G100 Thin")
    assert style.unparsable_tokens == ["144", "G100"]

    style = instance_parse("Loud Thin Italic")
    assert style.unparsable_tokens == ["Loud"]


def test_token_order():
    style = instance_parse("Italic Black")
    assert style.raw_token_order == ["ital", "wght"]
    assert style.expected_token_order == ["wght", "ital"]
