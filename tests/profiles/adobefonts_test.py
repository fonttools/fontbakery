import os

from fontTools.ttLib import TTFont
from fontbakery.checkrunner import (PASS, WARN, FAIL)
from fontbakery.codetesting import (get_check,
                                    portable_path,
                                    TEST_FILE,
                                    assert_PASS,
                                    assert_results_contain)
from fontbakery.profiles import adobefonts as adobefonts_profile

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
    assert_PASS(check(test_fonts))

    # now try with one font with a different UPM (i.e. 2048)
    test_fonts[1]['head'].unitsPerEm = 2048
    assert_results_contain(check(test_fonts),
                           FAIL, None) # FIXME: This needs a message keyword


def test_check_family_consistent_upm_new_style():
    # these fonts have a consistent unitsPerEm of 1000:
    filenames = ['SourceSansPro-Regular.otf',
                 'SourceSansPro-Bold.otf',
                 'SourceSansPro-It.otf']
    fonts = [os.path.join(portable_path("data/test/source-sans-pro/OTF"), filename)
                 for filename in filenames]
    from fontbakery.codetesting import FontsTestingContext
    check = FontsTestingContext(adobefonts_profile,
                      'com.adobe.fonts/check/family/consistent_upm',
                      fonts)


    # try fonts with consistent UPM (i.e. 1000)
    assert_PASS(check())

    ttFonts = check.args['ttFonts']
    # now try with one font with a different UPM (i.e. 2048)
    ttFonts[1]['head'].unitsPerEm = 2048
    assert_results_contain(check(),
                           FAIL, None) # FIXME: This needs a message keyword

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
                                                                 # or should we have
                                                                 # a get_superfamily_checks() method?
    }
    assert family_check_ids == expected_family_check_ids


def test_check_find_empty_letters():
    check = get_check(adobefonts_profile,
                      "com.adobe.fonts/check/find_empty_letters")

    # this font has inked glyphs for all letters
    font = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    assert_PASS(check(font))

    # this font has empty glyphs for several letters,
    # the first of which is 'B' (U+0042)
    font = TEST_FILE('familysans/FamilySans-Regular.ttf')
    message = assert_results_contain(check(font),
                                     FAIL, None) # FIXME:
                                                 # This needs a message keyword
    assert message == "U+0042 should be visible, but its glyph ('B') is empty."


def test_check_missing_whitespace():
    """ Check that overridden test for nbsp yields WARN rather than FAIL. """
    check = get_check(adobefonts_profile,
                      "com.google.fonts/check/whitespace_glyphs:adobefonts")

    font = TEST_FILE('source-sans-pro/OTF/SourceSansPro-Regular.otf')
    ttFont = TTFont(font)
    assert_PASS(check(ttFont))

    # remove U+00A0, status should be WARN (standard check would be FAIL)
    for subtable in ttFont['cmap'].tables:
        subtable.cmap.pop(0x00A0, None)
    assert_results_contain(check(ttFont),
                           WARN, None) # FIXME: This needs a message keyword

