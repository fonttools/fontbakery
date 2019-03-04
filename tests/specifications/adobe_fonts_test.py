from fontbakery.checkrunner import (PASS, FAIL)
from fontTools.ttLib import TTFont


def test_check_name_empty_records():
    """ Checking OS/2.usWeightClass """
    from fontbakery.specifications.adobe_fonts import (
        com_adobe_fonts_check_name_empty_records as check)
    font_path = "data/test/source-sans-pro/OTF/SourceSansPro-Regular.otf"
    test_font = TTFont(font_path)

    # try a font with fully populated name records
    status, message = list(check(test_font))[-1]
    assert status == PASS

    # now try a completely empty string
    test_font['name'].names[3].string = b''
    status, message = list(check(test_font))[-1]
    assert status == FAIL

    # now try a string that only has whitespace
    test_font['name'].names[3].string = b' '
    status, message = list(check(test_font))[-1]
    assert status == FAIL
