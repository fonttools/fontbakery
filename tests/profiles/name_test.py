import os
from types import SimpleNamespace

import fontTools.ttLib
from fontTools.ttLib import TTFont

from fontbakery.constants import (NameID,
                                  PlatformID,
                                  WindowsEncodingID,
                                  WindowsLanguageID,
                                  MacintoshEncodingID,
                                  MacintoshLanguageID)
from fontbakery.checkrunner import (INFO, WARN, PASS, FAIL)
from fontbakery.codetesting import (assert_PASS,
                                    assert_results_contain,
                                    CheckTester,
                                    portable_path,
                                    TEST_FILE)
from fontbakery.profiles import opentype as opentype_profile


def test_check_name_empty_records():
    check = CheckTester(opentype_profile,
                        "com.adobe.fonts/check/name/empty_records")

    font_path = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    test_font = TTFont(font_path)

    assert_PASS(check(test_font),
                'with a font with fully populated name records.')

    test_font['name'].names[3].string = b''
    assert_results_contain(check(test_font),
                           FAIL, 'empty-record',
                           'with a completely empty string.')

    test_font['name'].names[3].string = b' '
    assert_results_contain(check(test_font),
                           FAIL, 'empty-record',
                           'with a string that only has whitespace.')


def test_check_name_no_copyright_on_description():
    """ Description strings in the name table
        must not contain copyright info.
    """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/name/no_copyright_on_description")

    # Our reference Mada Regular is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # here we add a "Copyright" string to a NameID.DESCRIPTION
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.DESCRIPTION:
            ttFont['name'].names[i].string = "Copyright".encode(name.getEncoding())

    assert_results_contain(check(ttFont),
                           FAIL, 'copyright-on-description',
                           'with a bad font...')


def test_check_monospace():
    """ Checking correctness of monospaced metadata. """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/monospace")
    import string
    from fontbakery.constants import (PANOSE_Proportion,
                                      IsFixedWidth)

    # This check has a large number of code-paths
    # We'll make sure to test them all here.
    #
    # --------------------------------------------
    # Starting with non-monospaced code-paths:
    # --------------------------------------------

    # Our reference Mada Regular is a non-monospace font
    # know to have good metadata for this check.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           PASS, "good",
                           'with a good non-monospace font...')

    # We'll mark it as monospaced on the post table and make sure it fails:
    ttFont["post"].isFixedPitch = 42 # *any* non-zero value means monospaced
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-post-isFixedPitch',
                           'with a non-monospaced font with bad'
                           ' post.isFixedPitch value ...')

    # restore good value:
    ttFont["post"].isFixedPitch = IsFixedWidth.NOT_MONOSPACED

    # Now we mark it as monospaced on the OS/2 table and it should also fail:
    original_proportion = ttFont["OS/2"].panose.bProportion
    ttFont["OS/2"].panose.bProportion = PANOSE_Proportion.MONOSPACED
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-panose',
                           'with a non-monospaced font with bad'
                           ' OS/2.panose.bProportion value (MONOSPACED) ...')

    # restore good value
    ttFont["OS/2"].panose.bProportion = original_proportion

    # Now we try with very little ASCII characters in the font
    cmap = ttFont["cmap"]
    for subtable in list(cmap.tables):
        # Remove A-Z, a-z from cmap
        for code in list(map(ord, string.ascii_letters)):
            if subtable.cmap.get(code):
                del subtable.cmap[code]
    assert_results_contain(check(ttFont),
                           PASS, "good",
                           'with a good non-monospace font...')

    # --------------------------------------------
    # And now we test the monospaced code-paths:
    # --------------------------------------------

    print('Test PASS with a good monospaced font...')
    # Our reference OverpassMono Regular is know to be
    # a monospaced font with good metadata here.
    ttFont = TTFont(TEST_FILE("overpassmono/OverpassMono-Regular.ttf"))

    status, message = check(ttFont)[-1]
    # WARN is emitted when there's at least one outlier.
    # I don't see a good reason to be picky and also test that one separately here...
    assert (status == WARN and message.code == "mono-outliers") or \
           (status == PASS and message.code == "mono-good")

    # Let's incorrectly mark it as a non-monospaced on the post table and it should fail:
    ttFont["post"].isFixedPitch = IsFixedWidth.NOT_MONOSPACED
    # here we search for the expected FAIL among all results
    # instead of simply looking at the last one
    # because we may also get an outliers WARN in some cases:
    assert_results_contain(check(ttFont),
                           FAIL, 'mono-bad-post-isFixedPitch',
                           'with a monospaced font with'
                           ' bad post.isFixedPitch value ...')

    # There are several bad panose proportion values for a monospaced font.
    # Only PANOSE_Proportion.MONOSPACED would be valid.
    # So we'll try all the bad ones here to make sure all of them emit a FAIL:
    bad_monospaced_panose_values = [
        PANOSE_Proportion.ANY,
        PANOSE_Proportion.NO_FIT,
        PANOSE_Proportion.OLD_STYLE,
        PANOSE_Proportion.MODERN,
        PANOSE_Proportion.EVEN_WIDTH,
        PANOSE_Proportion.EXTENDED,
        PANOSE_Proportion.CONDENSED,
        PANOSE_Proportion.VERY_EXTENDED,
        PANOSE_Proportion.VERY_CONDENSED,
    ]
    for bad_value in bad_monospaced_panose_values:
        ttFont["OS/2"].panose.bProportion = bad_value
        # again, we search the expected FAIL because we may algo get an outliers WARN here:
        assert_results_contain(check(ttFont),
                               FAIL, 'mono-bad-panose',
                               f'Test FAIL with a monospaced font with bad'
                               f' OS/2.panose.bProportion value ({bad_value}) ...')

    # restore good values
    ttFont["post"].isFixedPitch = 1
    ttFont["OS/2"].panose.bProportion = PANOSE_Proportion.MONOSPACED

    # Now we try with very little ASCII characters in the font
    cmap = ttFont["cmap"]
    for subtable in list(cmap.tables):
        # Remove A-Z, a-z from cmap
        for code in list(map(ord, string.ascii_letters)):
            if subtable.cmap.get(code):
                del subtable.cmap[code]

    status, message = check(ttFont)[-1]
    # WARN is emitted when there's at least one outlier.
    # I don't see a good reason to be picky and also test that one separately here...
    assert (status == WARN and message.code == "mono-outliers") or \
           (status == PASS and message.code == "mono-good")


def test_check_name_match_familyname_fullfont():
    """ Does full font name begin with the font family name? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/name/match_familyname_fullfont")
    # Our reference Mada Regular is known to be good
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # alter the full-font-name prepending a bad prefix:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            ttFont["name"].names[i].string = "bad-prefix".encode(name.getEncoding())

    # and make sure the check FAILs:
    assert_results_contain(check(ttFont),
                           FAIL, 'does-not',
                           'with a font in which the family name'
                           ' begins with a digit...')

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            del ttFont["name"].names[i]
    assert_results_contain(check(ttFont),
                           FAIL, 'no-full-font-name',
                           'with no FULL_FONT_NAME entries...')

    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            del ttFont["name"].names[i]
    assert_results_contain(check(ttFont),
                           FAIL, 'no-font-family-name',
                           'with no FONT_FAMILY_NAME entries...')


def assert_name_table_check_result(ttFont, index, name, check, value, expected_result, expected_keyword=None):
    backup = name.string
    # set value
    ttFont["name"].names[index].string = value.encode(name.getEncoding())
    # run check
    status, message = list(check(ttFont))[-1]
    # restore value
    ttFont["name"].names[index].string = backup
    assert status == expected_result
    if expected_keyword:
        assert message.code == expected_keyword


def test_check_family_naming_recommendations():
    """ Font follows the family naming recommendations ? """
    check = CheckTester(opentype_profile,
                        "com.google.fonts/check/family_naming_recommendations")

    # Our reference Mada Medium is known to be good
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # We'll test rule violations in all entries one-by-one
    for index, name in enumerate(ttFont["name"].names):
        # and we'll test all INFO/PASS code-paths for each of the rules:
        def name_test(value, expected, keyword=None):
            assert_name_table_check_result(ttFont, index, name, check, value, expected, keyword) #pylint: disable=cell-var-from-loop

        if name.nameID == NameID.POSTSCRIPT_NAME:
            print ("== NameID.POST_SCRIPT_NAME ==")

            print ("Test INFO: May contain only a-zA-Z0-9 characters and an hyphen...")
            # The '@' and '!' chars here are the expected rule violations:
            name_test("B@zinga!", INFO, "bad-entries")

            print ("Test PASS: A name with a single hyphen is OK...")
            # A single hypen in the name is OK:
            name_test("Big-Bang", PASS)

            print ("Test INFO: May not contain more than a single hyphen...")
            # The second hyphen char here is the expected rule violation:
            name_test("Big-Bang-Theory", INFO, "bad-entries")

            print ("Test INFO: Exceeds max length (63)...")
            name_test("A"*64, INFO, "bad-entries")

            print ("Test PASS: Does not exceed max length...")
            name_test("A"*63, PASS)

        elif name.nameID == NameID.FULL_FONT_NAME:
            print ("== NameID.FULL_FONT_NAME ==")

            print ("Test INFO: Exceeds max length (63)...")
            name_test("A"*64, INFO, "bad-entries")

            print ("Test PASS: Does not exceeds max length...")
            name_test("A"*63, PASS)

        elif name.nameID == NameID.FONT_FAMILY_NAME:
            print ("== NameID.FONT_FAMILY_NAME ==")

            print ("Test INFO: Exceeds max length (31)...")
            name_test("A"*32, INFO, "bad-entries")

            print ("Test PASS: Does not exceeds max length...")
            name_test("A"*31, PASS)

        elif name.nameID == NameID.FONT_SUBFAMILY_NAME:
            print ("== NameID.FONT_SUBFAMILY_NAME ==")

            print ("Test INFO: Exceeds max length (31)...")
            name_test("A"*32, INFO, "bad-entries")

            print ("Test PASS: Does not exceeds max length...")
            name_test("A"*31, PASS)

        elif name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
            print ("== NameID.TYPOGRAPHIC_FAMILY_NAME ==")

            print ("Test INFO: Exceeds max length (31)...")
            name_test("A"*32, INFO, "bad-entries")

            print ("Test PASS: Does not exceeds max length...")
            name_test("A"*31, PASS)

        elif name.nameID == NameID.TYPOGRAPHIC_SUBFAMILY_NAME:
            print ("== NameID.FONT_TYPOGRAPHIC_SUBFAMILY_NAME ==")

            print ("Test INFO: Exceeds max length (31)...")
            name_test("A"*32, INFO, "bad-entries")

            print ("Test PASS: Does not exceeds max length...")
            name_test("A"*31, PASS)


def test_check_name_postscript_vs_cff():
    check = CheckTester(opentype_profile,
                        "com.adobe.fonts/check/name/postscript_vs_cff")
    test_font = TTFont()
    test_font['CFF '] = fontTools.ttLib.newTable('CFF ')
    test_font['CFF '].cff.fontNames = ['SomeFontName']
    test_font['name'] = fontTools.ttLib.newTable('name')

    test_font['name'].setName(
        'SomeOtherFontName',
        NameID.POSTSCRIPT_NAME,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA
    )

    test_font.reader = SimpleNamespace(file=SimpleNamespace(name="whatever"))
    assert_results_contain(check(test_font),
                           FAIL, 'mismatch')

    test_font['name'].setName(
        'SomeFontName',
        NameID.POSTSCRIPT_NAME,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA
    )
    assert_PASS(check(test_font))


def test_check_name_postscript_name_consistency():
    check = CheckTester(opentype_profile,
                        "com.adobe.fonts/check/name/postscript_name_consistency")

    base_path = portable_path("data/test/source-sans-pro/TTF")
    font_path = os.path.join(base_path, 'SourceSansPro-Regular.ttf')
    test_font = TTFont(font_path)

    # SourceSansPro-Regular only has one name ID 6 entry (for Windows),
    # let's add another one for Mac that matches the Windows entry:
    test_font['name'].setName(
        'SourceSansPro-Regular',
        NameID.POSTSCRIPT_NAME,
        PlatformID.MACINTOSH,
        MacintoshEncodingID.ROMAN,
        MacintoshLanguageID.ENGLISH
    )
    assert_PASS(check(test_font))

    # ...now let's change the Mac name ID 6 entry to something else:
    test_font['name'].setName(
        'YetAnotherFontName',
        NameID.POSTSCRIPT_NAME,
        PlatformID.MACINTOSH,
        MacintoshEncodingID.ROMAN,
        MacintoshLanguageID.ENGLISH
    )
    assert_results_contain(check(test_font),
                           FAIL, 'inconsistency')


def test_check_family_max_4_fonts_per_family_name():
    check = CheckTester(opentype_profile,
                        "com.adobe.fonts/check/family/max_4_fonts_per_family_name")

    base_path = portable_path("data/test/source-sans-pro/OTF")

    font_names = [
        'SourceSansPro-Black.otf',
        'SourceSansPro-BlackItalic.otf',
        'SourceSansPro-Bold.otf',
        'SourceSansPro-BoldItalic.otf',
        'SourceSansPro-ExtraLight.otf',
        'SourceSansPro-ExtraLightItalic.otf',
        'SourceSansPro-Italic.otf',
        'SourceSansPro-Light.otf',
        'SourceSansPro-LightItalic.otf',
        'SourceSansPro-Regular.otf',
        'SourceSansPro-Semibold.otf',
        'SourceSansPro-SemiboldItalic.otf']

    font_paths = [os.path.join(base_path, n) for n in font_names]

    test_fonts = [TTFont(x) for x in font_paths]

    # try fonts with correct family name grouping
    assert_PASS(check(test_fonts))

    # now set 5 of the fonts to have the same family name
    for font in test_fonts[:5]:
        name_records = font['name'].names
        for name_record in name_records:
            if name_record.nameID == 1:
                # print(repr(name_record.string))
                name_record.string = 'foobar'.encode('utf-16be')

    assert_results_contain(check(test_fonts),
                           FAIL, 'too-many')

