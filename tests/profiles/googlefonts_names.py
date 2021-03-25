from fontbakery.profiles.googlefonts_names import GFNameData
from fontTools.ttLib import TTFont
from fontbakery.codetesting import TEST_FILE
import pytest


@pytest.mark.parametrize(
    "font_path,family_name,subfamily_name,typo_family_name,typo_subfamily_name,filename,weight_class",
    [
        # Montserrat static fonts. We know this family is correct
        (
            TEST_FILE("montserrat/Montserrat-Black.ttf"),
            "Montserrat Black",
            "Regular",
            "Montserrat",
            "Black",
            "Montserrat-Black.ttf",
            900
        ),
        (
            TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
            "Montserrat Black",
            "Italic",
            "Montserrat",
            "Black Italic",
            "Montserrat-BlackItalic.ttf",
            900
        ),
        (TEST_FILE("montserrat/Montserrat-Bold.ttf"), "Montserrat", "Bold", None, None, "Montserrat-Bold.ttf", 700),
        (
            TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
            "Montserrat",
            "Bold Italic",
            None,
            None,
            "Montserrat-BoldItalic.ttf",
            700
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
            "Montserrat ExtraBold",
            "Regular",
            "Montserrat",
            "ExtraBold",
            "Montserrat-ExtraBold.ttf",
            800
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
            "Montserrat ExtraBold",
            "Italic",
            "Montserrat",
            "ExtraBold Italic",
            "Montserrat-ExtraBoldItalic.ttf",
            800
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
            "Montserrat ExtraLight",
            "Regular",
            "Montserrat",
            "ExtraLight",
            "Montserrat-ExtraLight.ttf",
            200
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
            "Montserrat ExtraLight",
            "Italic",
            "Montserrat",
            "ExtraLight Italic",
            "Montserrat-ExtraLightItalic.ttf",
            200
        ),
        (
            TEST_FILE("montserrat/Montserrat-Italic.ttf"),
            "Montserrat",
            "Italic",
            None,
            None,
            "Montserrat-Italic.ttf",
            400
        ),
        (
            TEST_FILE("montserrat/Montserrat-Light.ttf"),
            "Montserrat Light",
            "Regular",
            "Montserrat",
            "Light",
            "Montserrat-Light.ttf",
            300
        ),
        (
            TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
            "Montserrat Light",
            "Italic",
            "Montserrat",
            "Light Italic",
            "Montserrat-LightItalic.ttf",
            300
        ),
        (
            TEST_FILE("montserrat/Montserrat-Medium.ttf"),
            "Montserrat Medium",
            "Regular",
            "Montserrat",
            "Medium",
            "Montserrat-Medium.ttf",
            500
        ),
        (
            TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
            "Montserrat Medium",
            "Italic",
            "Montserrat",
            "Medium Italic",
            "Montserrat-MediumItalic.ttf",
            500
        ),
        (
            TEST_FILE("montserrat/Montserrat-Regular.ttf"),
            "Montserrat",
            "Regular",
            None,
            None,
            "Montserrat-Regular.ttf",
            400
        ),
        (
            TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
            "Montserrat SemiBold",
            "Regular",
            "Montserrat",
            "SemiBold",
            "Montserrat-SemiBold.ttf",
            600
        ),
        (
            TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
            "Montserrat SemiBold",
            "Italic",
            "Montserrat",
            "SemiBold Italic",
            "Montserrat-SemiBoldItalic.ttf",
            600
        ),
        (
            TEST_FILE("montserrat/Montserrat-Thin.ttf"),
            "Montserrat Thin",
            "Regular",
            "Montserrat",
            "Thin",
            "Montserrat-Thin.ttf",
            100
        ),
        (
            TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
            "Montserrat Thin",
            "Italic",
            "Montserrat",
            "Thin Italic",
            "Montserrat-ThinItalic.ttf",
            100
        ),
        # Recursive static fonts are good and contain interesting combinations
        (
            TEST_FILE("recursive/Recursive_Monospace-SemiBold.ttf"),
            "Recursive Monospace SemiBold",
            "Regular",
            "Recursive Monospace",
            "SemiBold",
            "RecursiveMonospace-SemiBold.ttf",
            600
        ),
        (
            TEST_FILE("recursive/Recursive_Monospace,Casual-ExtraBold.ttf"),
            "Recursive Monospace Casual ExtraBold",
            "Regular",
            "Recursive Monospace Casual",
            "ExtraBold",
            "RecursiveMonospaceCasual-ExtraBold.ttf",
            800
        ),
        # Let's check some variable fonts
        (
            # Open Sans fvar dflts: wght=300, wdth=75
            TEST_FILE("varfont/OpenSans[wdth,wght].ttf"),
            "Open Sans Condensed Light",
            "Regular",
            "Open Sans",
            "Condensed Light",
            "OpenSans[wdth,wght].ttf",
            300
        ),
        (
            # Oswald fvar dflts: wght=400
            TEST_FILE("varfont/Oswald-VF.ttf"),
            "Oswald",
            "Regular",
            None,
            None,
            "Oswald[wght].ttf",
            400
        ),
        (
            # Jura fvar dflts: wght=333
            TEST_FILE("varfont/jura/Jura[wght].ttf"),
            "Jura Light",
            "Regular",
            "Jura",
            "Light",
            "Jura[wght].ttf",
            300
        ),
        (
            # Newsreader fvar dflts: wght: 400, opsz: 18
            TEST_FILE("varfont/Newsreader[opsz,wght].ttf"),
            "Newsreader 18pt",
            "Regular",
            "Newsreader",
            "18pt Regular",
            "Newsreader[opsz,wght].ttf",
            400
        ),
        (
            # Newsreader fvar dflts: wght: 400, opsz: 18
            TEST_FILE("varfont/Newsreader-Italic[opsz,wght].ttf"),
            "Newsreader 18pt",
            "Italic",
            "Newsreader",
            "18pt Italic",
            "Newsreader-Italic[opsz,wght].ttf",
            400
        ),
    ],
)
def test_names_for_correct_fonts(
    font_path, family_name, subfamily_name, typo_family_name, typo_subfamily_name, filename, weight_class
):
    ttFont = TTFont(font_path)
    gfnames = GFNameData(ttFont)
    assert family_name == gfnames.family
    assert subfamily_name == gfnames.subFamily
    assert typo_family_name == gfnames.typoFamily
    assert typo_subfamily_name == gfnames.typoSubFamily
    assert filename == gfnames.filename
    assert weight_class == gfnames.usWeightClass
