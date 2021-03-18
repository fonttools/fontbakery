from fontbakery.profiles.googlefonts_names import GFSpec
from fontTools.ttLib import TTFont
from fontbakery.codetesting import TEST_FILE
import pytest


@pytest.mark.parametrize(
    "font_path,family_name,subfamily_name,typo_family_name,typo_subfamily_name",
    [
        # Montserrat static fonts. We know this family is correct
        (
            TEST_FILE("montserrat/Montserrat-Black.ttf"),
            "Montserrat Black",
            "Regular",
            "Montserrat",
            "Black",
        ),
        (
            TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
            "Montserrat Black",
            "Italic",
            "Montserrat",
            "Black Italic",
        ),
        (TEST_FILE("montserrat/Montserrat-Bold.ttf"), "Montserrat", "Bold", None, None),
        (
            TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
            "Montserrat",
            "Bold Italic",
            None,
            None,
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
            "Montserrat ExtraBold",
            "Regular",
            "Montserrat",
            "ExtraBold",
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
            "Montserrat ExtraBold",
            "Italic",
            "Montserrat",
            "ExtraBold Italic",
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
            "Montserrat ExtraLight",
            "Regular",
            "Montserrat",
            "ExtraLight",
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
            "Montserrat ExtraLight",
            "Italic",
            "Montserrat",
            "ExtraLight Italic",
        ),
        (
            TEST_FILE("montserrat/Montserrat-Italic.ttf"),
            "Montserrat",
            "Italic",
            None,
            None,
        ),
        (
            TEST_FILE("montserrat/Montserrat-Light.ttf"),
            "Montserrat Light",
            "Regular",
            "Montserrat",
            "Light",
        ),
        (
            TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
            "Montserrat Light",
            "Italic",
            "Montserrat",
            "Light Italic",
        ),
        (
            TEST_FILE("montserrat/Montserrat-Medium.ttf"),
            "Montserrat Medium",
            "Regular",
            "Montserrat",
            "Medium",
        ),
        (
            TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
            "Montserrat Medium",
            "Italic",
            "Montserrat",
            "Medium Italic",
        ),
        (
            TEST_FILE("montserrat/Montserrat-Regular.ttf"),
            "Montserrat",
            "Regular",
            None,
            None,
        ),
        (
            TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
            "Montserrat SemiBold",
            "Regular",
            "Montserrat",
            "SemiBold",
        ),
        (
            TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
            "Montserrat SemiBold",
            "Italic",
            "Montserrat",
            "SemiBold Italic",
        ),
        (
            TEST_FILE("montserrat/Montserrat-Thin.ttf"),
            "Montserrat Thin",
            "Regular",
            "Montserrat",
            "Thin",
        ),
        (
            TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
            "Montserrat Thin",
            "Italic",
            "Montserrat",
            "Thin Italic",
        ),
        # Recursive static fonts are good and contain interesting combinations
        (
            TEST_FILE("recursive/Recursive_Monospace-SemiBold.ttf"),
            "Recursive Monospace SemiBold",
            "Regular",
            "Recursive Monospace",
            "SemiBold",
        ),
        (
            TEST_FILE("recursive/Recursive_Monospace,Casual-ExtraBold.ttf"),
            "Recursive Monospace Casual ExtraBold",
            "Regular",
            "Recursive Monospace Casual",
            "ExtraBold",
        ),
    ],
)
def test_names_for_correct_fonts(
    font_path, family_name, subfamily_name, typo_family_name, typo_subfamily_name
):
    ttFont = TTFont(font_path)
    gfspec = GFSpec(ttFont)
    assert family_name == gfspec.family
    assert subfamily_name == gfspec.subFamily
    assert typo_family_name == gfspec.typoFamily
    assert typo_subfamily_name == gfspec.typoSubFamily
