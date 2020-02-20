import os

from fontTools.ttLib import TTFont
from fontbakery.checkrunner import (PASS, FAIL)
from fontbakery.utils import TEST_FILE


def test_check_family_consistent_upm():
    from fontbakery.profiles.adobefonts import (
        com_adobe_fonts_check_family_consistent_upm as check)

    base_path = TEST_FILE("source-sans-pro/OTF")

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
    from fontbakery.profiles.adobefonts import profile
    family_checks = profile.get_family_checks()
    family_check_ids = {check.id for check in family_checks}
    expected_family_check_ids = {
        # RIBBI: 'com.adobe.fonts/check/family/bold_italic_unique_for_nameid1',
        'com.adobe.fonts/check/family/consistent_upm',
        'com.adobe.fonts/check/family/max_4_fonts_per_family_name',
        'com.google.fonts/check/family/underline_thickness',
        'com.google.fonts/check/family/panose_proportion',
        'com.google.fonts/check/family/panose_familytype',
        'com.google.fonts/check/family/equal_unicode_encodings',
        'com.google.fonts/check/family/equal_font_versions',
        'com.google.fonts/check/family/win_ascent_and_descent',
        'com.google.fonts/check/family/vertical_metrics',
        # 'com.google.fonts/check/superfamily/vertical_metrics', # should it be included here?
                                                                 # or should we have a get_superfamily_checks() method?
    }
    assert family_check_ids == expected_family_check_ids


def test_check_find_empty_letters():
    from fontbakery.profiles.adobefonts import \
        com_adobe_fonts_check_find_empty_letters as check

    # this font has inked glyphs for all letters
    font_path = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    test_font = TTFont(font_path)
    status, message = list(check(test_font))[-1]
    assert status == PASS

    # this font has empty glyphs for several letters
    font_path = TEST_FILE('familysans/FamilySans-Regular.ttf')
    test_font = TTFont(font_path)

    expected_message = "U+007A should be visible, but its glyph ('z') is empty."
    status, message = list(check(test_font))[-1]
    assert status == FAIL
    assert message == expected_message
