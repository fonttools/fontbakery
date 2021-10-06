import io
import os
import pytest

import fontTools.ttLib
from fontTools.ttLib import TTFont
import fontTools.subset

from fontbakery.checkrunner import (INFO, WARN, FAIL)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    portable_path,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


mada_fonts = [
    TEST_FILE("mada/Mada-Black.ttf"),
    TEST_FILE("mada/Mada-ExtraLight.ttf"),
    TEST_FILE("mada/Mada-Medium.ttf"),
    TEST_FILE("mada/Mada-SemiBold.ttf"),
    TEST_FILE("mada/Mada-Bold.ttf"),
    TEST_FILE("mada/Mada-Light.ttf"),
    TEST_FILE("mada/Mada-Regular.ttf")
]

@pytest.fixture
def mada_ttFonts():
    return [TTFont(path) for path in mada_fonts]

cabin_fonts = [
    TEST_FILE("cabin/Cabin-BoldItalic.ttf"),
    TEST_FILE("cabin/Cabin-Bold.ttf"),
    TEST_FILE("cabin/Cabin-Italic.ttf"),
    TEST_FILE("cabin/Cabin-MediumItalic.ttf"),
    TEST_FILE("cabin/Cabin-Medium.ttf"),
    TEST_FILE("cabin/Cabin-Regular.ttf"),
    TEST_FILE("cabin/Cabin-SemiBoldItalic.ttf"),
    TEST_FILE("cabin/Cabin-SemiBold.ttf")
]


def test_check_family_panose_proportion(mada_ttFonts):
    """ Fonts have consistent PANOSE proportion ? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/family/panose_proportion")

    assert_PASS(check(mada_ttFonts),
                'with good family.')

    # introduce a wrong value in one of the font files:
    value = mada_ttFonts[0]['OS/2'].panose.bProportion
    incorrect_value = value + 1
    mada_ttFonts[0]['OS/2'].panose.bProportion = incorrect_value

    assert_results_contain(check(mada_ttFonts),
                           FAIL, 'inconsistency',
                           'with inconsistent family.')


def test_check_family_panose_familytype(mada_ttFonts):
    """ Fonts have consistent PANOSE family type ? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/family/panose_familytype")

    assert_PASS(check(mada_ttFonts),
                'with good family.')

    # introduce a wrong value in one of the font files:
    value = mada_ttFonts[0]['OS/2'].panose.bFamilyType
    incorrect_value = value + 1
    mada_ttFonts[0]['OS/2'].panose.bFamilyType = incorrect_value

    assert_results_contain(check(mada_ttFonts),
                           FAIL, 'inconsistency',
                           'with inconsistent family.')


def test_check_xavgcharwidth():
    """ Check if OS/2 xAvgCharWidth is correct. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/xavgcharwidth")

    test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    test_font['OS/2'].xAvgCharWidth = 556
    assert_results_contain(check(test_font),
                           INFO, "xAvgCharWidth-close")

    test_font['OS/2'].xAvgCharWidth = 500
    assert_results_contain(check(test_font),
                           WARN, "xAvgCharWidth-wrong") # FIXME: This needs a message keyword

    del test_font['OS/2']
    del test_font['glyf']
    del test_font['hmtx']
    test_font['OS/2'] = fontTools.ttLib.newTable('OS/2')
    test_font['OS/2'].version = 4
    test_font['OS/2'].xAvgCharWidth = 1000
    test_font['glyf'] = fontTools.ttLib.newTable('glyf')
    test_font['glyf'].glyphs = {}
    test_font['hmtx'] = fontTools.ttLib.newTable('hmtx')
    test_font['hmtx'].metrics = {}
    assert_results_contain(check(test_font),
                           FAIL, 'missing-glyphs')

    test_font = TTFont(test_font_path)
    subsetter = fontTools.subset.Subsetter()
    subsetter.populate(glyphs=['a', 'b', 'c', 'd', 'e', 'f', 'g',
                               'h', 'i', 'j', 'k', 'l', 'm', 'n',
                               'o', 'p', 'q', 'r', 's', 't', 'u',
                               'v', 'w', 'x', 'y', 'z', 'space'])
    subsetter.subset(test_font)
    test_font['OS/2'].xAvgCharWidth = 447
    test_font['OS/2'].version = 2
    temp_file = io.BytesIO()
    test_font.save(temp_file)
    test_font = TTFont(temp_file)
    test_font.reader.file.name = "foo.ttf"
    assert_PASS(check(test_font))

    test_font['OS/2'].xAvgCharWidth = 450
    assert_results_contain(check(test_font),
                           INFO, "xAvgCharWidth-close")

    test_font['OS/2'].xAvgCharWidth = 500
    assert_results_contain(check(test_font),
                           WARN, "xAvgCharWidth-wrong")

    test_font = TTFont(temp_file)
    test_font.reader.file.name = "foo.ttf"
    subsetter = fontTools.subset.Subsetter()
    subsetter.populate(glyphs=['b', 'c', 'd', 'e', 'f', 'g', 'h',
                               'i', 'j', 'k', 'l', 'm', 'n', 'o',
                               'p', 'q', 'r', 's', 't', 'u', 'v',
                               'w', 'x', 'y', 'z', 'space'])
    subsetter.subset(test_font)
    assert_results_contain(check(test_font),
                           FAIL, 'missing-glyphs')


def test_check_fsselection_matches_macstyle():
    """Check if OS/2 fsSelection matches head macStyle bold and italic bits."""
    check = CheckTester(opentype_profile,
                        "com.adobe.fonts/check/fsselection_matches_macstyle")
    from fontbakery.constants import FsSelection

    test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

    # try a regular (not bold, not italic) font
    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    # now turn on bold in OS/2.fsSelection, but not in head.macStyle
    test_font['OS/2'].fsSelection |= FsSelection.BOLD
    message = assert_results_contain(check(test_font),
                                     FAIL, "fsselection-macstyle-bold")
    assert 'bold' in message

    # now turn off bold in OS/2.fsSelection so we can focus on italic
    test_font['OS/2'].fsSelection &= ~FsSelection.BOLD

    # now turn on italic in OS/2.fsSelection, but not in head.macStyle
    test_font['OS/2'].fsSelection |= FsSelection.ITALIC
    message = assert_results_contain(check(test_font),
                                     FAIL, "fsselection-macstyle-italic")
    assert 'italic' in message


def test_check_family_bold_italic_unique_for_nameid1():
    """Check that OS/2.fsSelection bold/italic settings are unique within each
    Compatible Family group (i.e. group of up to 4 with same NameID1)"""
    check = CheckTester(opentype_profile,
                        "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1")
    from fontbakery.constants import FsSelection

    base_path = portable_path("data/test/source-sans-pro/OTF")

    # these fonts have the same NameID1
    font_names = ['SourceSansPro-Regular.otf',
                  'SourceSansPro-Bold.otf',
                  'SourceSansPro-Italic.otf',
                  'SourceSansPro-BoldItalic.otf']
    font_paths = [os.path.join(base_path, n) for n in font_names]
    ttFonts = [TTFont(x) for x in font_paths]

    # the family should be correctly constructed
    assert_PASS(check(ttFonts))

    # now hack the italic font to also have the bold bit set
    ttFonts[2]['OS/2'].fsSelection |= FsSelection.BOLD

    # we should get a failure due to two fonts with both bold & italic set
    message = assert_results_contain(check(ttFonts),
                                     FAIL, "unique-fsselection")
    assert message == ("Family 'Source Sans Pro' has 2 fonts (should be no"
                       " more than 1) with the same OS/2.fsSelection"
                       " bold & italic settings: Bold=True, Italic=True")


def test_check_code_pages():
    """ Check code page character ranges """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/code_pages")

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert(ttFont['OS/2'].ulCodePageRange1 != 0 or
           ttFont['OS/2'].ulCodePageRange2 != 0) # It has got at least 1 code page range declared
    assert_PASS(check(ttFont),
                'with good font.')

    ttFont['OS/2'].ulCodePageRange1 = 0 # remove all code pages to make the check FAIL
    ttFont['OS/2'].ulCodePageRange2 = 0
    assert_results_contain(check(ttFont),
                           FAIL, "no-code-pages",
                           'with a font with no code page declared.')

