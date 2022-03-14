import pytest
import io
import os
from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (INFO, WARN, FAIL)
from fontbakery.codetesting import (assert_PASS,
                                    assert_SKIP,
                                    assert_results_contain,
                                    CheckTester,
                                    TEST_FILE)
from fontbakery.constants import NameID
from fontbakery.profiles import universal as universal_profile


@pytest.fixture
def montserrat_ttFonts():
    paths = [
        TEST_FILE("montserrat/Montserrat-Black.ttf"),
        TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Bold.ttf"),
        TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Italic.ttf"),
        TEST_FILE("montserrat/Montserrat-Light.ttf"),
        TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Medium.ttf"),
        TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Regular.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Thin.ttf"),
        TEST_FILE("montserrat/Montserrat-ThinItalic.ttf")
    ]
    return [TTFont(path) for path in paths]


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

cabin_condensed_fonts = [
    TEST_FILE("cabincondensed/CabinCondensed-Regular.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-Medium.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-Bold.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-SemiBold.ttf")
]

@pytest.fixture
def cabin_ttFonts():
    return [TTFont(path) for path in cabin_fonts]

@pytest.fixture
def cabin_condensed_ttFonts():
    return [TTFont(path) for path in cabin_condensed_fonts]


def test_check_valid_glyphnames():
    """ Glyph names are all valid? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/valid_glyphnames")

    # We start with a good font file:
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # There used to be a 31 char max-length limit.
    # This was considered good:
    ttFont.glyphOrder[2] = "a" * 31
    assert_PASS(check(ttFont))

    # And this was considered bad:
    legacy_too_long = "a" * 32
    ttFont.glyphOrder[2] = legacy_too_long
    message = assert_results_contain(check(ttFont),
                                     WARN, 'legacy-long-names')
    assert legacy_too_long in message

    # Nowadays, it seems most implementations can deal with
    # up to 63 char glyph names:
    good_name = "b" * 63
    bad_name1 = "a" * 64
    bad_name2 = "3cents"
    bad_name3 = ".threecents"
    ttFont.glyphOrder[2] = bad_name1
    ttFont.glyphOrder[3] = bad_name2
    ttFont.glyphOrder[4] = bad_name3
    ttFont.glyphOrder[5] = good_name
    message = assert_results_contain(check(ttFont),
                                     FAIL, 'found-invalid-names')
    assert good_name not in message
    assert bad_name1 in message
    assert bad_name2 in message
    assert bad_name3 in message

    # TrueType fonts with a format 3.0 post table contain
    # no glyph names, so the check must be SKIP'd in that case.
    #
    # Upgrade to post format 3.0 and roundtrip data to update TTF object.
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont["post"].formatType = 3.0
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    assert_SKIP(check(ttFont))


def test_check_unique_glyphnames():
    """ Font contains unique glyph names? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/unique_glyphnames")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # Fonttools renames duplicate glyphs with #1, #2, ... on load.
    # Code snippet from https://github.com/fonttools/fonttools/issues/149.
    glyph_names = ttFont.getGlyphOrder()
    glyph_names[2] = glyph_names[3]

    # Load again, we changed the font directly.
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.setGlyphOrder(glyph_names)
    ttFont['post']  # Just access the data to make fonttools generate it.
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_results_contain(check(ttFont),
                                     FAIL, "duplicated-glyph-names")
    assert "space" in message

    # Upgrade to post format 3.0 and roundtrip data to update TTF object.
    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    ttFont.setGlyphOrder(glyph_names)
    ttFont["post"].formatType = 3.0
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    assert_SKIP(check(ttFont))


def DISABLED_test_check_glyphnames_max_length():
    """ Check that glyph names do not exceed max length. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/glyphnames_max_length")
    import defcon
    import ufo2ft

    # TTF
    test_font = defcon.Font(TEST_FILE("test.ufo"))
    ttFont = ufo2ft.compileTTF(test_font)
    assert_PASS(check(ttFont))

    test_glyph = defcon.Glyph()
    test_glyph.unicode = 0x1234
    test_glyph.name = ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                       "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                       "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    test_font.insertGlyph(test_glyph)
    ttFont = ufo2ft.compileTTF(test_font, useProductionNames=False)
    assert_results_contain(check(ttFont),
                           FAIL, "glyphname-too-long")


    ttFont = ufo2ft.compileTTF(test_font, useProductionNames=True)
    assert_PASS(check(ttFont))


    # Upgrade to post format 3.0 and roundtrip data to update TTF object.
    ttFont["post"].formatType = 3.0
    _file = io.BytesIO()
    _file.name = ttFont.reader.file.name
    ttFont.save(_file)
    ttFont = TTFont(_file)
    message = assert_PASS(check(ttFont))
    assert "format 3.0" in message

    del test_font, ttFont, _file  # Prevent copypasta errors.

    # CFF
    test_font = defcon.Font(TEST_FILE("test.ufo"))
    ttFont = ufo2ft.compileOTF(test_font)
    assert_PASS(check(ttFont))

    test_font.insertGlyph(test_glyph)
    ttFont = ufo2ft.compileOTF(test_font, useProductionNames=False)
    assert_results_contain(check(ttFont),
                           FAIL, "glyphname-too-long")

    ttFont = ufo2ft.compileOTF(test_font, useProductionNames=True)
    assert_PASS(check(ttFont))


def test_check_ttx_roundtrip():
    """ Checking with fontTools.ttx """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/ttx-roundtrip")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font))

    # TODO: Can anyone show us a font file that fails ttx roundtripping?!
    #
    # font = TEST_FILE("...")
    # assert_results_contain(check(font),
    #                        FAIL, None) # FIXME: This needs a message keyword


def test_is_up_to_date():
    from fontbakery.profiles.universal import is_up_to_date
    # is_up_to_date(installed, latest)
    assert(is_up_to_date(installed="0.5.0",
                            latest="0.5.0") == True)
    assert(is_up_to_date(installed="0.5.1",
                            latest="0.5.0") == True)
    assert(is_up_to_date(installed="0.4.1",
                            latest="0.5.0") == False)
    assert(is_up_to_date(installed="0.3.4",
                            latest="0.3.5") == False)
    assert(is_up_to_date(installed="1.0.0",
                            latest="1.0.1") == False)
    assert(is_up_to_date(installed="2.0.0",
                            latest="1.5.3") == True)
    assert(is_up_to_date(installed="0.5.2.dev73+g8c9ebc0.d20181023",
                            latest="0.5.1") == True)
    assert(is_up_to_date(installed="0.5.2.dev73+g8c9ebc0.d20181023",
                            latest="0.5.2") == False)
    assert(is_up_to_date(installed="0.5.2.dev73+g8c9ebc0.d20181023",
                            latest="0.5.3") == False)


def test_check_name_trailing_spaces():
    """ Name table entries must not have trailing spaces. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/name/trailing_spaces")

    # Our reference Cabin Regular is known to be good:
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    for i, entry in enumerate(ttFont['name'].names):
        good_string = ttFont['name'].names[i].toUnicode()
        bad_string = good_string + " "
        ttFont['name'].names[i].string = bad_string.encode(entry.getEncoding())
        assert_results_contain(check(ttFont),
                               FAIL, "trailing-space",
                               f'with a bad name table entry ({i}: "{bad_string}")...')

        #restore good entry before moving to the next one:
        ttFont['name'].names[i].string = good_string.encode(entry.getEncoding())


def test_check_family_single_directory():
    """ Fonts are all in the same directory. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/family/single_directory")
    same_dir = [
        TEST_FILE("cabin/Cabin-Thin.ttf"),
        TEST_FILE("cabin/Cabin-ExtraLight.ttf")
    ]
    multiple_dirs = [
        TEST_FILE("mada/Mada-Regular.ttf"),
        TEST_FILE("cabin/Cabin-ExtraLight.ttf")
    ]

    assert_PASS(check(same_dir),
                f'with same dir: {same_dir}')

    assert_results_contain(check(multiple_dirs),
                           FAIL, "single-directory",
                           f'with multiple dirs: {multiple_dirs}')


def test_check_ots():
    """ Checking with ots-sanitize. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/ots")

    sanitary_font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(sanitary_font))

    bogus_font = TEST_FILE("README.txt")
    message = assert_results_contain(check(bogus_font),
                                     FAIL, "ots-sanitize-error")
    assert "invalid sfntVersion" in message
    assert "Failed to sanitize file!" in message


def test_check_mandatory_glyphs():
    """ Font contains the first few mandatory glyphs (.null or NULL, CR and space)? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/mandatory_glyphs")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    import fontTools.subset
    subsetter = fontTools.subset.Subsetter()
    subsetter.populate(glyphs="n")  # Arbitrarily remove everything except n.
    subsetter.subset(ttFont)
    # It seems that fontTools automatically adds '.notdef' as the 1st glyph
    # but as an empty one, so the check should complain about it:
    assert_results_contain(check(ttFont),
                           WARN, 'empty')
    # FIXME: The assumption above should be double-checked!


    # TODO: assert_results_contain(check(ttFont),
    #                              WARN, 'codepoint')

    # TODO: assert_results_contain(check(ttFont),
    #                              WARN, 'first-glyph')


def test_check_whitespace_glyphs():
    """ Font contains glyphs for whitespace characters? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/whitespace_glyphs")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # We remove the nbsp char (0x00A0)
    for table in ttFont['cmap'].tables:
        if 0x00A0 in table.cmap:
            del table.cmap[0x00A0]

    # And make sure the problem is detected:
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-whitespace-glyph-0x00A0',
                           'with a font lacking a nbsp (0x00A0)...')

    # restore original Mada Regular font:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # And finally do the same with the space character (0x0020):
    for table in ttFont['cmap'].tables:
        if 0x0020 in table.cmap:
            del table.cmap[0x0020]
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-whitespace-glyph-0x0020',
                           'with a font lacking a space (0x0020)...')


def test_check_whitespace_glyphnames():
    """ Font has **proper** whitespace glyph names? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/whitespace_glyphnames")

    def deleteGlyphEncodings(font, cp):
        """ This routine is used on to introduce errors
            in a given font by removing specific entries
            in the cmap tables.
        """
        for subtable in font['cmap'].tables:
            if subtable.isUnicode():
                subtable.cmap = {
                    codepoint: name for codepoint, name in subtable.cmap.items()
                    if codepoint != cp
                }

    def editCmap(font, cp, name):
        """ Corrupt the cmap by changing the glyph name
            for a given code point.
        """
        for subtable in font['cmap'].tables:
            if subtable.isUnicode():
                # Copy the map
                subtable.cmap = subtable.cmap.copy()
                # edit it
                subtable.cmap[cp] = name

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')


    value = ttFont["post"].formatType
    ttFont["post"].formatType = 3.0
    assert_SKIP(check(ttFont),
                'with post.formatType == 3.0 ...')

    # restore good value:
    ttFont["post"].formatType = value


    deleteGlyphEncodings(ttFont, 0x0020)
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-0020',
                           'with missing glyph name for char 0x0020 ...')


    # restore the original font object in preparation for the next test-case:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    deleteGlyphEncodings(ttFont, 0x00A0)
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-00a0',
                           'with missing glyph name for char 0x00A0 ...')


    # restore the original font object in preparation for the next test-case:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # See https://github.com/googlefonts/fontbakery/issues/2624
    # nbsp is not Adobe Glyph List compliant.
    editCmap(ttFont, 0x00A0, "nbsp")
    assert_results_contain(check(ttFont),
                           FAIL, 'non-compliant-00a0',
                           'with not AGL-compliant glyph name "nbsp" for char 0x00A0...')


    editCmap(ttFont, 0x00A0, "nbspace")
    assert_results_contain(check(ttFont),
                           WARN, 'not-recommended-00a0',
                           'for naming 0x00A0 "nbspace"...')


    editCmap(ttFont, 0x0020, "foo")
    assert_results_contain(check(ttFont),
                           FAIL, 'non-compliant-0020',
                           'with not AGL-compliant glyph name "foo" for char 0x0020...')


    editCmap(ttFont, 0x0020, "uni0020")
    assert_results_contain(check(ttFont),
                           WARN, 'not-recommended-0020',
                           'for naming 0x0020 "uni0020"...')


    editCmap(ttFont, 0x0020, "space")
    editCmap(ttFont, 0x00A0, "uni00A0")
    assert_PASS(check(ttFont))


def test_check_whitespace_ink():
    """ Whitespace glyphs have ink? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/whitespace_ink")

    test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font["cmap"].tables[0].cmap[0x1680] = "a"
    assert_PASS(check(test_font),
                'because Ogham space mark does have ink.')

    test_font["cmap"].tables[0].cmap[0x0020] = "uni1E17"
    assert_results_contain(check(test_font),
                           FAIL, 'has-ink',
                           'for whitespace character having composites (with ink).')

    test_font["cmap"].tables[0].cmap[0x0020] = "scedilla"
    assert_results_contain(check(test_font),
                           FAIL, 'has-ink',
                           'for whitespace character having outlines (with ink).')

    import fontTools.pens.ttGlyphPen
    pen = fontTools.pens.ttGlyphPen.TTGlyphPen(test_font.getGlyphSet())
    pen.addComponent("space", (1, 0, 0, 1, 0, 0))
    test_font["glyf"].glyphs["uni200B"] = pen.glyph()
    assert_results_contain(check(test_font),
                           FAIL, 'has-ink', # should we give is a separate keyword? This looks wrong.
                           'for whitespace character having composites (without ink).')


def test_check_required_tables():
    """ Font contains all required tables ? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/required_tables")

    required_tables = ["cmap", "head", "hhea", "hmtx",
                       "maxp", "name", "OS/2", "post"]
    optional_tables = ["cvt ", "fpgm", "loca", "prep",
                       "VORG", "EBDT", "EBLC", "EBSC",
                       "BASE", "GPOS", "GSUB", "JSTF",
                       "gasp", "hdmx", "kern", "LTSH",
                       "PCLT", "VDMX", "vhea", "vmtx"]
    # Our reference Mada Regular font is good here
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # Now we test the special cases for variable fonts:
    #
    # Note: A TTF with an fvar table but no STAT table
    #       is probably a GX font. For now we're OK with
    #       rejecting those by emitting a FAIL in this case.
    #
    # TODO: Maybe we could someday emit a more explicit
    #       message to the users regarding that...
    ttFont.reader.tables["fvar"] = "foo"
    assert_results_contain(check(ttFont),
                           FAIL, "required-tables",
                           'with fvar but no STAT...')

    del ttFont.reader.tables["fvar"]
    ttFont.reader.tables["STAT"] = "foo"
    assert_PASS(check(ttFont),
                'with STAT on a non-variable font...')

    # and finally remove what we've just added:
    del ttFont.reader.tables["STAT"]
    # Now we remove required tables one-by-one to validate the FAIL code-path:
    for required in required_tables:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        if required in ttFont.reader.tables:
            del ttFont.reader.tables[required]
        assert_results_contain(check(ttFont),
                               FAIL, "required-tables",
                               f'with missing mandatory table {required} ...')
    # Then, in preparation for the next step, we make sure
    # there's no optional table (by removing them all):
    for optional in optional_tables:
        if optional in ttFont.reader.tables:
            del ttFont.reader.tables[optional]

    # Then re-insert them one by one to validate the INFO code-path:
    for optional in optional_tables:
        ttFont.reader.tables[optional] = "foo"
        # and ensure that the second to last logged message is an
        # INFO status informing the user about it:
        assert_results_contain(check(ttFont),
                               INFO, "optional-tables",
                               f'with optional table {required} ...')
        # remove the one we've just inserted before trying the next one:
        del ttFont.reader.tables[optional]


def test_check_unwanted_tables():
    """ Are there unwanted tables ? """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/unwanted_tables")

    unwanted_tables = [
        "FFTM", # FontForge
        "TTFA", # TTFAutohint
        "TSI0", # TSI* = VTT
        "TSI1",
        "TSI2",
        "TSI3",
        "TSI5",
        "prop", # FIXME: Why is this one unwanted?
    ]
    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # We now add unwanted tables one-by-one to validate the FAIL code-path:
    for unwanted in unwanted_tables:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        ttFont.reader.tables[unwanted] = "foo"
        assert_results_contain(check(ttFont),
                               FAIL, "unwanted-tables",
                               f'with unwanted table {unwanted} ...')


def test_glyph_has_ink():
    from fontbakery.utils import glyph_has_ink
    from fontTools.ttLib import TTFont

    print()  # so next line doesn't start with '.....'

    cff_test_font = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf"))
    print('Test if CFF glyph with ink has ink')
    assert(glyph_has_ink(cff_test_font, '.notdef') is True)
    print('Test if CFF glyph without ink has ink')
    assert(glyph_has_ink(cff_test_font, 'space') is False)

    ttf_test_font = TTFont(TEST_FILE("source-sans-pro/TTF/SourceSansPro-Regular.ttf"))
    print('Test if TTF glyph with ink has ink')
    assert(glyph_has_ink(ttf_test_font, '.notdef') is True)
    print('Test if TTF glyph without ink has ink')
    assert(glyph_has_ink(ttf_test_font, 'space') is False)

    cff2_test_font = TTFont(TEST_FILE("source-sans-pro/VAR/SourceSansVariable-Roman.otf"))
    print('Test if CFF2 glyph with ink has ink')
    assert(glyph_has_ink(cff2_test_font, '.notdef') is True)
    print('Test if CFF2 glyph without ink has ink')
    assert(glyph_has_ink(cff2_test_font, 'space') is False)


mada_fonts = [
    TEST_FILE("mada/Mada-Black.ttf"),
    TEST_FILE("mada/Mada-ExtraLight.ttf"),
    TEST_FILE("mada/Mada-Medium.ttf"),
    TEST_FILE("mada/Mada-SemiBold.ttf"),
    TEST_FILE("mada/Mada-Bold.ttf"),
    TEST_FILE("mada/Mada-Light.ttf"),
    TEST_FILE("mada/Mada-Regular.ttf"),
]

@pytest.fixture
def mada_ttFonts():
    return [TTFont(path) for path in mada_fonts]


def test_check_family_win_ascent_and_descent(mada_ttFonts):
    """ Checking OS/2 usWinAscent & usWinDescent. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/family/win_ascent_and_descent")
    from fontbakery.profiles.shared_conditions import vmetrics

    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # But we fix it first to test the PASS code-path:
    vm = vmetrics(mada_ttFonts)
    ttFont['OS/2'].usWinAscent = vm['ymax']
    ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
    assert_PASS(check(ttFont),
                'with a good font...')

    # Then we break it:
    ttFont['OS/2'].usWinAscent = 0 # FIXME: this should be bad as well: vm['ymax'] - 1
    ttFont['OS/2'].usWinDescent = abs(vm['ymin'])
    assert_results_contain(check(ttFont),
                           FAIL, 'ascent',
                           'with a bad OS/2.usWinAscent...')

    # and also this other way of breaking it:
    ttFont['OS/2'].usWinAscent = vm['ymax']
    ttFont['OS/2'].usWinDescent = 0 # FIXME: this should be bad as well: abs(vm['ymin']) - 1
    assert_results_contain(check(ttFont),
                           FAIL, 'descent',
                           'with a bad OS/2.usWinDescent...')


def test_check_os2_metrics_match_hhea(mada_ttFonts):
    """ Checking OS/2 Metrics match hhea Metrics. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/os2_metrics_match_hhea")

    # Our reference Mada Regular is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    assert_PASS(check(ttFont),
                'with a good font...')

    # Now we break it:
    correct = ttFont['hhea'].ascent
    ttFont['OS/2'].sTypoAscender = correct + 1
    assert_results_contain(check(ttFont),
                           FAIL, 'ascender',
                           'with a bad OS/2.sTypoAscender font...')

    # Restore good value:
    ttFont['OS/2'].sTypoAscender = correct

    # And break it again, now on sTypoDescender value:
    correct = ttFont['hhea'].descent
    ttFont['OS/2'].sTypoDescender = correct + 1
    assert_results_contain(check(ttFont),
                           FAIL, 'descender',
                           'with a bad OS/2.sTypoDescender font...')


def test_check_family_vertical_metrics(montserrat_ttFonts):
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/family/vertical_metrics")

    assert_PASS(check(montserrat_ttFonts),
                'with multiple good fonts...')

    montserrat_ttFonts[0]['OS/2'].usWinAscent = 4000
    assert_results_contain(check(montserrat_ttFonts),
                           FAIL, 'usWinAscent-mismatch',
                           'with one bad font that has one different vertical metric val...')

    # TODO: Also test these code-paths:
    # FAIL, 'mismatch-<other values>'
    # FAIL, 'lacks-OS/2'
    # FAIL, 'lacks-hhea'


def test_check_superfamily_vertical_metrics(montserrat_ttFonts, cabin_ttFonts, cabin_condensed_ttFonts):
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/superfamily/vertical_metrics")

    assert_PASS(check([], {"superfamily_ttFonts": [cabin_ttFonts,
                                                   cabin_condensed_ttFonts]}),
                'with multiple good families...')

    assert_results_contain(check([], {"superfamily_ttFonts": [cabin_ttFonts,
                                                              montserrat_ttFonts]}),
                           WARN, "superfamily-vertical-metrics",
                           'with families that diverge on vertical metric values...')


def test_check_STAT_strings():
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/STAT_strings")

    good = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_PASS(check(good))

    bad = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Italic.ttf"))
    assert_results_contain(check(bad),
                           FAIL, "bad-italic")


def test_check_rupee():
    """ Ensure indic fonts have the Indian Rupee Sign glyph. """
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/rupee")

    # FIXME: This should be possible:
    #          The `assert_SKIP` helper should be able to detect when a
    #          check skips due to unmet @conditions.
    #          For now it only detects explicit SKIP messages instead.
    #
    # non_indic = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    # assert_SKIP(check(non_indic),
    #             "with a non-indic font.")
    #
    #        But for now we have to do this:
    #
    from fontbakery.profiles.shared_conditions import is_indic_font
    print("Ensure the check will SKIP when dealing with a non-indic font...")
    non_indic = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert is_indic_font(non_indic) == False


    # This one is good:
    ttFont = TTFont(TEST_FILE("indic-font-with-rupee-sign/NotoSerifDevanagari-Regular.ttf"))
    assert_PASS(check(ttFont),
                "with a sample font that has the Indian Rupee Sign.")

    # But this one lacks the glyph:
    ttFont = TTFont(TEST_FILE("indic-font-without-rupee-sign/NotoSansOlChiki-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           FAIL, "missing-rupee",
                           "with a sample font missing it.")


def test_check_unreachable_glyphs():
    """Check font contains no unreachable glyphs."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/unreachable_glyphs")

    font = TEST_FILE("noto_sans_tamil_supplement/NotoSansTamilSupplement-Regular.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    message = assert_results_contain(check(font), WARN, "unreachable-glyphs")
    for glyph in [
        "Gtilde",
        "eight.dnom",
        "four.dnom",
        "three.dnom",
        "two.dnom",
        "i.dot",
        "five.numr",
        "seven.numr",
        "bullet.cap",
        "periodcentered.cap",
        "ampersand.sc",
        "I.uc",
    ]:
        assert glyph in message

    for glyph in [
        "caronvertical",
        "acute.cap",
        "breve.cap",
        "caron.cap",
        "circumflex.cap",
        "dotaccent.cap",
        "dieresis.cap",
        "grave.cap",
        "hungarumlaut.cap",
        "macron.cap",
        "ring.cap",
        "tilde.cap",
        "breve.r",
        "breve.rcap",
    ]:
        assert glyph not in message


def test_check_contour_count(montserrat_ttFonts):
    """Check glyphs contain the recommended contour count"""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/contour_count")
    # TODO: FAIL, "lacks-cmap"

    for ttFont in montserrat_ttFonts:
        # Montserrat which was used to assemble the glyph data,
        # so, it should be good, except for that softhyphen...
        # TODO: how can we test PASS then?
        assert_results_contain(check(ttFont),
                               WARN, 'softhyphen')

    # Lets swap the glyf 'a' (2 contours) with glyf 'c' (1 contour)
    for ttFont in montserrat_ttFonts:
        ttFont['glyf']['a'] = ttFont['glyf']['c']
        assert_results_contain(check(ttFont),
                               WARN, 'contour-count')


def test_check_cjk_chws_feature():
    """Does the font contain chws and vchw features?"""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/cjk_chws_feature")

    cjk_font = TEST_FILE("cjk/SourceHanSans-Regular.otf")
    ttFont = TTFont(cjk_font)
    assert_results_contain(check(ttFont),
                           FAIL, "missing-chws-feature",
                           'for Source Han Sans')

    assert_results_contain(check(ttFont),
                           FAIL, "missing-vchw-feature",
                           'for Source Han Sans')

    # Insert them.
    from fontTools.ttLib.tables.otTables import FeatureRecord
    chws = FeatureRecord()
    chws.FeatureTag = "chws"
    vchw = FeatureRecord()
    vchw.FeatureTag = "vchw"
    ttFont["GPOS"].table.FeatureList.FeatureRecord.extend([chws, vchw])

    assert_PASS(check(ttFont))


def test_check_designspace_has_sources():
    """See if we can actually load the source files."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/designspace_has_sources")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_PASS(check(designspace))

    # TODO: FAIL, 'no-sources'


def test_check_designspace_has_default_master():
    """Ensure a default master is defined."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/designspace_has_default_master")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_PASS(check(designspace))

    # TODO: FAIL, 'not-found'


def test_check_designspace_has_consistent_glyphset():
    """Check consistency of glyphset in a designspace file."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/designspace_has_consistent_glyphset")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_results_contain(check(designspace),
                           FAIL, 'inconsistent-glyphset')

    # TODO: Fix it and ensure it passes the check


def test_check_designspace_has_consistent_codepoints():
    """Check codepoints consistency in a designspace file."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/designspace_has_consistent_codepoints")

    designspace = TEST_FILE("stupidfont/Stupid Font.designspace")
    assert_results_contain(check(designspace),
                           FAIL, 'inconsistent-codepoints')

    # TODO: Fix it and ensure it passes the check


def test_check_transformed_components():
    """Ensure component transforms do not perform scaling or rotation."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/transformed_components")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                "with a good font...")

    # DM Sans v1.100 had some transformed components
    font = TEST_FILE("dm-sans-v1.100/DMSans-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, 'transformed-components')


def test_check_dotted_circle():
    """Ensure dotted circle glyph is present and can attach marks."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/dotted_circle")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font),
                "with a good font...")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font),
                           WARN, "missing-dotted-circle")

    font = TEST_FILE("broken_markazitext/MarkaziText-VF.ttf")
    assert_results_contain(check(font),
                           FAIL, "unattached-dotted-circle-marks")


def test_check_gsub5_gpos7():
    """Check if font contains any GSUB 5 or GPOS 7 lookups
    which are not widely supported."""
    check = CheckTester(universal_profile,
                        "com.google.fonts/check/gsub5_gpos7")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(font),
                "with a good font...")

    font = TEST_FILE("notosanskhudawadi/NotoSansKhudawadi-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, "has-gsub5")

    assert_results_contain(check(font),
                           FAIL, "has-gpos7")
