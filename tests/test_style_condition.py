from fontbakery.codetesting import TEST_FILE
from fontbakery.testable import Font


def test_style_condition():
    expectations = {
        "shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf": "Regular",
        "shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf": "Italic",
        "shantell/ShantellSans-FakeVFBold[BNCE,INFM,SPAC,wght].ttf": "Bold",
        "shantell/ShantellSans-FakeVFBoldItalic[BNCE,INFM,SPAC,wght].ttf": "BoldItalic",
        "bad_fonts/style_linking_issues/NotoSans-Regular.ttf": "Regular",
        "bad_fonts/style_linking_issues/NotoSans-Italic.ttf": "Italic",
        "bad_fonts/style_linking_issues/NotoSans-Bold.ttf": "Bold",
        "bad_fonts/style_linking_issues/NotoSans-BoldItalic.ttf": "BoldItalic",
        "bad_fonts/bad_stylenames/NotoSans-Fat.ttf": None,
        "bad_fonts/bad_stylenames/NotoSans.ttf": None,
    }
    for filename, expected in expectations.items():
        assert Font(TEST_FILE(filename)).style == expected
