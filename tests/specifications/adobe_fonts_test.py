import os

from fontTools.ttLib import TTFont
from fontbakery.checkrunner import (PASS, FAIL)


def test_check_name_empty_records():
    from fontbakery.specifications.adobe_fonts import (
        com_adobe_fonts_check_name_empty_records as check)
    font_path = os.path.join('data', 'test', 'source-sans-pro', 'OTF',
                             'SourceSansPro-Regular.otf')
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


def test_check_consistent_upm():
    from fontbakery.specifications.adobe_fonts import (
        com_adobe_fonts_check_consistent_upm as check)

    base_path = os.path.join('data', 'test', 'source-sans-pro', 'OTF')

    # these fonts have a consistent unitsPerEm of 1000:
    font_names = ['SourceSansPro-Regular.otf',
                  'SourceSansPro-Bold.otf',
                  'SourceSansPro-It.otf']

    font_paths = [os.path.join(base_path, n) for n in font_names]

    test_fonts = [TTFont(x) for x in font_paths]

    # try fonts with consistent UPM (i.e. 1000)
    status, message = list(check(test_fonts))[-1]
    assert status == PASS

    # now try with one font with a different UPM (i.e. 2048)
    test_fonts[1]['head'].unitsPerEm = 2048
    status, message = list(check(test_fonts))[-1]
    assert status == FAIL


def test_get_family_checks():
    from fontbakery.specifications.adobe_fonts import specification
    family_checks = specification.get_family_checks()
    family_check_ids = {check.id for check in family_checks}
    expected_family_check_ids = {
        'com.adobe.fonts/check/bold_italic_unique_for_nameid1',
        'com.adobe.fonts/check/consistent_upm',
        'com.adobe.fonts/check/max_4_fonts_per_family_name',
        'com.google.fonts/check/008',
        'com.google.fonts/check/009',
        'com.google.fonts/check/010',
        'com.google.fonts/check/013',
        'com.google.fonts/check/014',
        'com.google.fonts/check/040'
    }
    assert family_check_ids == expected_family_check_ids
