import pytest
import os
from fontTools.ttLib import TTFont

from fontbakery.checkrunner import (DEBUG, INFO, WARN, ERROR,
                                    SKIP, PASS, FAIL, ENDCHECK)
from fontbakery.codetesting import (assert_results_contain,
                                    assert_PASS,
                                    assert_SKIP,
                                    portable_path,
                                    TEST_FILE,
                                    GLYPHSAPP_TEST_FILE,
                                    CheckTester)
from fontbakery.configuration import Configuration
from fontbakery.constants import (NameID,
                                  PlatformID,
                                  WindowsEncodingID,
                                  WindowsLanguageID,
                                  MacintoshEncodingID,
                                  MacintoshLanguageID,
                                  OFL_BODY_TEXT)
from fontbakery.profiles import googlefonts as googlefonts_profile
import math

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

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

montserrat_fonts = [
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

cjk_font = TEST_FILE("cjk/SourceHanSans-Regular.otf")


@pytest.fixture
def montserrat_ttFonts():
    return [TTFont(path) for path in montserrat_fonts]

@pytest.fixture
def cabin_ttFonts():
    return [TTFont(path) for path in cabin_fonts]

@pytest.fixture
def vf_ttFont():
    path = TEST_FILE("varfont/Oswald-VF.ttf")
    return TTFont(path)


def change_name_table_id(ttFont, nameID, newEntryString, platEncID=0):
    for i, nameRecord in enumerate(ttFont['name'].names):
        if nameRecord.nameID == nameID and nameRecord.platEncID == platEncID:
            ttFont['name'].names[i].string = newEntryString

def delete_name_table_id(ttFont, nameID):
    delete = []
    for i, nameRecord in enumerate(ttFont['name'].names):
        if nameRecord.nameID == nameID:
            delete.append(i)
    for i in sorted(delete, reverse=True):
        del(ttFont['name'].names[i])

@pytest.fixture
def cabin_regular_path():
    return portable_path('data/test/cabin/Cabin-Regular.ttf')


def test_example_checkrunner_based(cabin_regular_path):
    """ This is just an example test. We'll probably need something like
        this setup in a checkrunner_test.py testsuite.
        Leave it here for the moment until we implemented a real case.

        This test is run via the checkRunner and demonstrate how to get
        (mutable) objects from the conditions cache and change them.

        NOTE: the actual fontbakery checks of conditions should never
        change a condition object.
    """
    from fontbakery.checkrunner import CheckRunner
    from fontbakery.profiles.googlefonts import profile
    values = dict(fonts=[cabin_regular_path])
    runner = CheckRunner(profile, values, Configuration(explicit_checks=['com.google.fonts/check/vendor_id']))

    # we could also reuse the `iterargs` that was assigned in the previous
    # for loop, but this here is more explicit
    iterargs = (('font', 0),)
    ttFont = runner.get('ttFont', iterargs)

    print('Test PASS ...')
    # prepare
    ttFont['OS/2'].achVendID = "APPL"
    # run
    for status, message, _ in runner.run():
        if status in check_statuses:
            last_check_message = message
        if status == ENDCHECK:
            assert message == PASS
            break

    print('Test WARN ...')
    # prepare
    ttFont['OS/2'].achVendID = "????"
    # run
    for status, message, _ in runner.run():
        if status in check_statuses:
            last_check_message = message
        if status == ENDCHECK:
            assert message == WARN and last_check_message.code == 'unknown'
            break


def test_check_canonical_filename():
    """ Files are named canonically. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/canonical_filename")

    static_canonical_names = [
        TEST_FILE("montserrat/Montserrat-Thin.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
        TEST_FILE("montserrat/Montserrat-Light.ttf"),
        TEST_FILE("montserrat/Montserrat-Regular.ttf"),
        TEST_FILE("montserrat/Montserrat-Medium.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
        TEST_FILE("montserrat/Montserrat-Bold.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
        TEST_FILE("montserrat/Montserrat-Black.ttf"),
        TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-Italic.ttf"),
        TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
        TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
    ]

    varfont_canonical_names = [
        TEST_FILE("cabinvfbeta/CabinVFBeta-Italic[wght].ttf"),
        TEST_FILE("cabinvfbeta/CabinVFBeta[wdth,wght].ttf"), # axis tags are sorted
    ]

    non_canonical_names = [
        TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"),
        TEST_FILE("cabinvfbeta/Cabin-Italic.ttf"),
        TEST_FILE("cabinvfbeta/Cabin-Roman.ttf"),
        TEST_FILE("cabinvfbeta/Cabin-Italic-VF.ttf"),
        TEST_FILE("cabinvfbeta/Cabin-Roman-VF.ttf"),
        TEST_FILE("cabinvfbeta/Cabin-VF.ttf"),
        TEST_FILE("cabinvfbeta/CabinVFBeta[wght,wdth].ttf"), # axis tags are NOT sorted here
    ]

    for canonical in static_canonical_names + varfont_canonical_names:
        assert_PASS(check(canonical),
                    f'with "{canonical}" ...')

    for non_canonical in non_canonical_names:
        assert_results_contain(check(non_canonical),
                               FAIL, 'bad-varfont-filename',
                               f'with "{non_canonical}" ...')

    assert_results_contain(check(TEST_FILE("Bad_Name.ttf")),
                           FAIL, 'invalid-char',
                           'with filename containing an underscore...')

    assert_results_contain(check(TEST_FILE("mutatorsans-vf/MutatorSans-VF.ttf")),
                           FAIL, 'unknown-name',
                           'with a variable font that lacks some important name table entries...')

    # TODO: FAIL, 'bad-static-filename'
    # TODO: FAIL, 'varfont-with-static-filename'


def test_check_description_broken_links():
    """ Does DESCRIPTION file contain broken links ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/broken_links")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                'with description file that has no links...')

    good_desc = check['description']
    good_desc += ("<a href='http://example.com'>Good Link</a>"
                  "<a href='http://fonts.google.com'>Another Good One</a>")
    assert_PASS(check(font, {"description": good_desc}),
                'with description file that has good links...')

    good_desc += "<a href='mailto:juca@members.fsf.org'>An example mailto link</a>"
    assert_results_contain(check(font, {"description": good_desc}),
                           INFO, "email",
                           'with a description file containing "mailto" links...')

    assert_PASS(check(font, {"description": good_desc}),
                      'with a description file containing "mailto" links...')

    bad_desc = good_desc + "<a href='http://thisisanexampleofabrokenurl.com/'>This is a Bad Link</a>"
    assert_results_contain(check(font, {"description": bad_desc}),
                           FAIL, 'broken-links',
                           'with a description file containing a known-bad URL...')

    #TODO: WARN, 'timeout'


def test_check_description_git_url():
    """ Does DESCRIPTION file contain an upstream Git repo URL? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/git_url")

    # TODO: test INFO 'url-found'

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, 'lacks-git-url',
                           'with description file that has no git repo URLs...')

    good_desc = ("<a href='https://github.com/uswds/public-sans'>Good URL</a>"
                 "<a href='https://gitlab.com/smc/fonts/uroob'>Another Good One</a>")
    assert_PASS(check(font, {"description": good_desc}),
                'with description file that has good links...')

    bad_desc = "<a href='https://v2.designsystem.digital.gov'>Bad URL</a>"
    assert_results_contain(check(font, {"description": bad_desc}),
                           FAIL, 'lacks-git-url',
                           'with description file that has false git in URL...')


def test_check_description_valid_html():
    """ DESCRIPTION file is a propper HTML snippet ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/valid_html")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font),
                'with description file that contains a good HTML snippet...')

    bad_desc = open(TEST_FILE("cabin/FONTLOG.txt"), "r").read() # :-)
    assert_results_contain(check(font, {"description": bad_desc}),
                           FAIL, 'lacks-paragraph',
                           'with a known-bad file (without HTML paragraph tags)...')

    bad_desc = "<html>foo</html>"
    assert_results_contain(check(font, {"description": bad_desc}),
                           FAIL, 'html-tag',
                           'with description file that contains the <html> tag...')

    bad_desc = ("<p>This example has the & caracter,"
                " but does not escape it with an HTML entity code."
                " It should use &amp; instead."
                "</p>")
    assert_results_contain(check(font, {"description": bad_desc}),
                           FAIL, 'malformed-snippet',
                           'with a known-bad file (not using HTML entity syntax)...')


def test_check_description_min_length():
    """ DESCRIPTION.en_us.html must have more than 200 bytes. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/min_length")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    bad_length = 'a' * 199
    assert_results_contain(check(font, {"description": bad_length}),
                           FAIL, 'too-short',
                           'with 199-byte buffer...')

    bad_length = 'a' * 200
    assert_results_contain(check(font, {"description": bad_length}),
                           FAIL, 'too-short',
                           'with 200-byte buffer...')

    good_length = 'a' * 201
    assert_PASS(check(font, {"description": good_length}),
                'with 201-byte buffer...')


def test_check_description_max_length():
    """ DESCRIPTION.en_us.html must have less than 2000 bytes. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/max_length")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    bad_length = 'a' * 2001
    assert_results_contain(check(font, {"description": bad_length}),
                           FAIL, "too-long",
                           'with 2001-byte buffer...')

    bad_length = 'a' * 2000
    assert_results_contain(check(font, {"description": bad_length}),
                           FAIL, "too-long",
                           'with 2000-byte buffer...')

    good_length = 'a' * 1999
    assert_PASS(check(font, {"description": good_length}),
                'with 1999-byte buffer...')


def test_check_description_eof_linebreak():
    """ DESCRIPTION.en_us.html should end in a linebreak. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/eof_linebreak")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    bad = ("We want to avoid description files\n"
           "without an end-of-file linebreak\n"
           "like this one.")
    assert_results_contain(check(font, {"description": bad}),
                           WARN, "missing-eof-linebreak",
                           'when we lack an end-of-file linebreak...')

    good = ("On the other hand, this one\n"
            "is good enough.\n")
    assert_PASS(check(font, {"description": good}),
                'when we add one...')


def test_check_name_family_and_style_max_length():
    """ Combined length of family and style must not exceed 27 characters. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/family_and_style_max_length")

    # Our reference Cabin Regular is known to be good 
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # Then we emit a WARNing with long family/style names
    # Originaly these were based on the example on the glyphs tutorial
    # (at https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances)
    # but later we increased a bit the max allowed length.

    # First we expect a WARN with a bad FAMILY NAME
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            # This has 28 chars, while the max currently allowed is 27.
            bad = "AnAbsurdlyLongFamilyNameFont"
            assert len(bad) == 28
            ttFont["name"].names[index].string = bad.encode(name.getEncoding())
            break
    assert_results_contain(check(ttFont),
                           WARN, 'too-long',
                           'with a bad font...')

    # Now let's restore the good Cabin Regular...
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # ...and break the check again with a bad SUBFAMILY NAME:
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_SUBFAMILY_NAME:
            bad = "WithAVeryLongAndBadStyleName"
            assert len(bad) == 28
            ttFont["name"].names[index].string = bad.encode(name.getEncoding())
            break
    assert_results_contain(check(ttFont),
                           WARN, 'too-long',
                           'with a bad font...')


def DISABLED_test_check_glyphs_file_name_family_and_style_max_length():
    """ Combined length of family and style must not exceed 27 characters. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/glyphs_file/name/family_and_style_max_length")

    # Our reference Comfortaa.glyphs is known to be good
    glyphsFile = GLYPHSAPP_TEST_FILE("Comfortaa.glyphs")

    # So it must PASS the check:
    assert_PASS(check(glyphsFile),
                'with a good font...')

    # Then we emit a WARNing with long family/style names
    # Originaly these were based on the example on the glyphs tutorial
    # (at https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances)
    # but later we increased a bit the max allowed length.

    # First we expect a WARN with a bad FAMILY NAME
    # This has 28 chars, while the max currently allowed is 27.
    bad = "AnAbsurdlyLongFamilyNameFont"
    assert len(bad) == 28
    glyphsFile.familyName = bad
    assert_results_contain(check(glyphsFile),
                           WARN, 'too-long',
                           'with a too long font familyname...')

    for i in range(len(glyphsFile.instances)):
        # Restore the good glyphs file...
        glyphsFile = GLYPHSAPP_TEST_FILE("Comfortaa.glyphs")

        # ...and break the check again with a long SUBFAMILY NAME
        # on one of its instances:
        bad_stylename = "WithAVeryLongAndBadStyleName"
        assert len(bad_stylename) == 28
        glyphsFile.instances[i].fullName = f"{glyphsFile.familyName} {bad_stylename}"
        assert_results_contain(check(glyphsFile),
                               WARN, 'too-long',
                               'with a too long stylename...')


def test_check_name_line_breaks():
    """ Name table entries should not contain line-breaks. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/line_breaks")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    num_entries = len(ttFont["name"].names)
    for i in range(num_entries):
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        encoding = ttFont["name"].names[i].getEncoding()
        ttFont["name"].names[i].string = "bad\nstring".encode(encoding)
        assert_results_contain(check(ttFont),
                               FAIL, 'line-break',
                               f'with name entries containing a linebreak ({i}/{num_entries})...')


def test_check_name_rfn():
    """ Name table strings must not contain 'Reserved Font Name'. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/rfn")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # The OFL text contains the term 'Reserved Font Name',
    # which should to cause a FAIL:
    ttFont["name"].setName(OFL_BODY_TEXT,
                           NameID.LICENSE_DESCRIPTION,
                           PlatformID.WINDOWS, WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    assert_PASS(check(ttFont),
                "with the OFL full text...")

    ttFont["name"].setName("Bla Reserved Font Name",
                           NameID.VERSION_STRING,
                           PlatformID.WINDOWS, WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(ttFont),
                           FAIL, 'rfn',
                           'with "Reserved Font Name" on a name table entry...')


def test_check_metadata_parses():
    """ Check METADATA.pb parse correctly. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/parses")

    good = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    assert_PASS(check(good),
                'with a good METADATA.pb file...')

    skip = TEST_FILE("slabo/Slabo-Regular.ttf")
    assert_results_contain(check(skip),
                           SKIP, 'file-not-found',
                           'with a missing METADATA.pb file...')

    bad = TEST_FILE("broken_metadata/foo.ttf")
    assert_results_contain(check(bad),
                           FAIL, 'parsing-error',
                           'with a bad METADATA.pb file...')


def test_check_metadata_unknown_designer():
    """ Font designer field in METADATA.pb must not be 'unknown'. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/unknown_designer")

    font = TEST_FILE("merriweather/Merriweather.ttf")
    assert_PASS(check(font),
                'with a good METADATA.pb file...')

    md = check["family_metadata"]
    md.designer = "unknown"
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'unknown-designer',
                           'with a bad METADATA.pb file...')


def test_check_metadata_designer_values():
    """ Multiple values in font designer field in
        METADATA.pb must be separated by commas. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/designer_values")

    font = TEST_FILE("merriweather/Merriweather.ttf")
    assert_PASS(check(font),
                'with a good METADATA.pb file...')

    md = check["family_metadata"]
    md.designer = "Pentagram, MCKL"
    assert_PASS(check(font, {"family_metadata": md}),
                'with a good multiple-designers string...')

    md.designer = "Pentagram / MCKL" # This actually happened on an
                                     # early version of the Red Hat Text family
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'slash',
                           'with a bad multiple-designers string'
                           ' (names separated by a slash char)...')


def test_check_metadata_broken_links():
    """ Does DESCRIPTION file contain broken links? """
    #check = CheckTester(googlefonts_profile,
    #                    "com.google.fonts/check/metadata/broken_links")
    # TODO: Implement-me!
    # INFO, "email"
    # WARN, "timeout"
    # FAIL, "broken-links"


def test_check_metadata_undeclared_fonts():
    """ Ensure METADATA.pb lists all font binaries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/undeclared_fonts")

    # Our reference Nunito family is know to be good here.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    # Our reference Cabin family has files that are not declared in its METADATA.pb:
    # - CabinCondensed-Medium.ttf
    # - CabinCondensed-SemiBold.ttf
    # - CabinCondensed-Regular.ttf
    # - CabinCondensed-Bold.ttf
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, 'file-not-declared')

    # We placed an additional file on a subdirectory of our reference
    # OverpassMono family with the name "another_directory/ThisShouldNotBeHere.otf"
    font = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_results_contain(check(font),
                           WARN, 'font-on-subdir')

    # We do accept statics folder though!
    # Jura is an example:
    font = TEST_FILE("varfont/jura/Jura.ttf")
    assert_PASS(check(font))


@pytest.mark.skip(reason="re-enable after addressing issue #1998")
def test_check_family_equal_numbers_of_glyphs(mada_ttFonts, cabin_ttFonts):
    """ Fonts have equal numbers of glyphs? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/family/equal_numbers_of_glyphs")

    # our reference Cabin family is know to be good here.
    assert_PASS(check(cabin_ttFonts),
                'with a good family.')

    # our reference Mada family is bad here with 407 glyphs on most font files
    # except the Black and the Medium, that both have 408 glyphs.
    assert_results_contain(check(mada_ttFonts),
                           FAIL, 'glyph-count-diverges',
                           'with fonts that diverge on number of glyphs.')


@pytest.mark.skip(reason="re-enable after addressing issue #1998")
def test_check_family_equal_glyph_names(mada_ttFonts, cabin_ttFonts):
    """ Fonts have equal glyph names? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/family/equal_glyph_names")

    # our reference Cabin family is know to be good here.
    assert_PASS(check(cabin_ttFonts),
                'with a good family.')

    # our reference Mada family is bad here with 407 glyphs on most font files
    # except the Black and the Medium, that both have 408 glyphs (that extra glyph
    # causes the check to fail).
    assert_results_contain(check(mada_ttFonts),
                           FAIL, 'missing-glyph',
                           'with fonts that diverge on number of glyphs.')


def test_check_fstype():
    """ Checking OS/2 fsType """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/fstype")

    # our reference Cabin family is know to be good here.
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font without DRM.')

    # modify the OS/2 fsType value to something different than zero:
    ttFont['OS/2'].fsType = 1

    assert_results_contain(check(ttFont),
                           FAIL, 'drm',
                           'with fonts that enable DRM restrictions via non-zero fsType bits.')


def test_condition__registered_vendor_ids():
    """ Get a list of vendor IDs from Microsoft's website. """
    from fontbakery.profiles.googlefonts import registered_vendor_ids
    registered_ids = registered_vendor_ids()

    print('As of July 2018, "MLAG": "Michael LaGattuta" must show up in the list...')
    assert "MLAG" in registered_ids # Michael LaGattuta

    print('As of December 2020, "GOOG": "Google" must show up in the list...')
    assert "GOOG" in registered_ids # Google

    print('"CFA ": "Computer Fonts Australia" is a good vendor id, lacking a URL')
    assert "CFA " in registered_ids # Computer Fonts Australia

    print('"GNU ": "Free Software Foundation, Inc." is a good vendor id with 3 letters and a space.')
    assert "GNU " in registered_ids # Free Software Foundation, Inc. / http://www.gnu.org/

    print('"GNU" without the right-padding space must not be on the list!')
    assert "GNU" not in registered_ids # All vendor ids must be 4 chars long!

    print('"ADBE": "Adobe" is a good 4-letter vendor id.')
    assert "ADBE" in registered_ids # Adobe

    print('"B&H ": "Bigelow & Holmes" is a valid vendor id that contains an ampersand.')
    assert "B&H " in registered_ids # Bigelow & Holmes

    print('"MS  ": "Microsoft Corp." is a good vendor id with 2 letters and padded with spaces.')
    assert "MS  " in registered_ids # Microsoft Corp.

    print('"TT\0\0": we also accept vendor-IDs containing NULL-padding.')
    assert "TT\0\0" in registered_ids # constains NULL bytes

    print('All vendor ids must be 4 chars long!')
    assert "GNU" not in registered_ids # 3 chars long is bad
    assert "MS" not in registered_ids # 2 chars long is bad
    assert "H" not in registered_ids # 1 char long is bad

    print('"H   ": "Hurme Design" is a good vendor id with a single letter padded with spaces.')
    assert "H   " in registered_ids # Hurme Design

    print('"   H": But not padded on the left, please!')
    assert "   H" not in registered_ids # a bad vendor id (presumably for "Hurme Design"
                                        # but with a vendor id parsing bug)

    print('"????" is an unknown vendor id.')
    assert "????" not in registered_ids


def test_check_vendor_id():
    """ Checking OS/2 achVendID """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/vendor_id")

    # Let's start with our reference Merriweather Regular
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    bad_vids = ['UKWN', 'ukwn', 'PfEd']
    for bad_vid in bad_vids:
        ttFont['OS/2'].achVendID = bad_vid
        assert_results_contain(check(ttFont),
                               WARN, 'bad',
                               f'with bad vid "{bad_vid}".')

    ttFont['OS/2'].achVendID = None
    assert_results_contain(check(ttFont),
                           WARN, 'not-set',
                           'with font missing vendor id info.')

    ttFont['OS/2'].achVendID = "????"
    assert_results_contain(check(ttFont),
                           WARN, 'unknown',
                           'with unknwon vendor id.')

    # we now change the fields into a known good vendor id:
    ttFont['OS/2'].achVendID = "APPL"
    assert_PASS(check(ttFont),
                'with a good font.')

    # And let's also make sure it works here:
    ttFont['OS/2'].achVendID = "GOOG"
    assert_PASS(check(ttFont),
                'with a good font.')


def NOT_IMPLEMENTED__test_check_glyph_coverage():
    """ Check glyph coverage. """
    #check = CheckTester(googlefonts_profile,
    #                    "com.google.fonts/check/glyph_coverage")
    #TODO: Implement-me!

    ## Our reference Mada Regular is know to be bad here.
    #ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    #assert_results_contain(check(ttFont),
    #                       FAIL, 'missing-codepoints',
    #                       'with a bad font...')

    ## Our reference Cabin Regular is know to be good here.
    #ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    #assert_PASS(check(ttFont),
    #            'with a good font...')


def test_check_name_unwanted_chars():
    """ Substitute copyright, registered and trademark
        symbols in name table entries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/unwanted_chars")

    # Our reference Mada Regular is know to be bad here.
    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, 'unwanted-chars',
                           'with a bad font...')

    # Our reference Cabin Regular is know to be good here.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                'with a good font...')


def test_check_usweightclass():
    """ Checking OS/2 usWeightClass. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/usweightclass")

    # Our reference Mada Regular is know to be bad here.
    font = TEST_FILE("mada/Mada-Regular.ttf")
    ttFont = TTFont(font)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-value',
                           f'with bad font "{font}" ...')

    # All fonts in our reference Cabin family are know to be good here.
    for font in cabin_fonts:
        ttFont = TTFont(font)
        assert_PASS(check(ttFont),
                    f'with good font "{font}"...')

    # Check otf Thin == 250 and ExtraLight == 275
    font = TEST_FILE("rokkitt/Rokkitt-Thin.otf")
    ttFont = TTFont(font)
    assert_results_contain(check(ttFont),
                           FAIL, "bad-value",
                           f'with bad font "{font}"...')

    ttFont['OS/2'].usWeightClass = 250
    assert_PASS(check(ttFont),
                f'with good font "{font}" (usWeightClass = 250) ...')

    font = TEST_FILE("rokkitt/Rokkitt-ExtraLight.otf")
    ttFont = TTFont(font)
    assert_results_contain(check(ttFont),
                           FAIL, "bad-value",
                           f'with bad font "{font}" ...')

    ttFont['OS/2'].usWeightClass = 275
    assert_PASS(check(ttFont),
                f'with good font "{font}" (usWeightClass = 275) ...')

    # TODO: test italic variants to ensure we do not get regressions of
    #       this bug: https://github.com/googlefonts/fontbakery/issues/2650


def test_family_directory_condition():
    from fontbakery.profiles.shared_conditions import family_directory
    assert family_directory("some_directory/Foo.ttf") == "some_directory"
    assert family_directory("some_directory/subdir/Foo.ttf") == "some_directory/subdir"
    assert family_directory("Foo.ttf") == "." # This is meant to ensure license files
                                              # are correctly detected on the current
                                              # working directory.

def test_check_family_has_license():
    """ Check font project has a license. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/family/has_license")

    from fontbakery.profiles.googlefonts import licenses

    # The lines maked with 'hack' below are meant to
    # not let fontbakery's own license to mess up
    # this code test.
    detected_licenses = licenses(portable_path("data/test/028/multiple"))
    detected_licenses.pop(-1) # hack
    assert_results_contain(check([], {"licenses": detected_licenses}),
                           FAIL, 'multiple',
                           'with multiple licenses...')

    detected_licenses = licenses(portable_path("data/test/028/none"))
    detected_licenses.pop(-1) # hack
    assert_results_contain(check([], {"licenses": detected_licenses}),
                           FAIL, 'no-license',
                           'with no license...')

    detected_licenses = licenses(portable_path("data/test/028/pass_ofl"))
    detected_licenses.pop(-1) # hack
    assert_PASS(check([], {"licenses": detected_licenses}),
                'with a single OFL license...')

    detected_licenses = licenses(portable_path("data/test/028/pass_apache"))
    detected_licenses.pop(-1) # hack
    assert_PASS(check([], {"licenses": detected_licenses}),
                'with a single Apache license...')


def test_check_license_ofl_body_text():
    """Check OFL.txt contains correct body text."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/license/OFL_body_text")

    # Our reference Montserrat family is know to have
    # a proper OFL.txt license file.
    # NOTE: This is currently considered good
    #       even though it uses an "http://" URL
    font = TEST_FILE("montserrat/Montserrat-Regular.ttf")
    ttFont = TTFont(font)

    assert_PASS(check(ttFont),
                'with a good OFL.txt license with "http://" url.')


    # using "https://" is also considered good:
    good_license = check["license_contents"].replace("http://", "https://")
    assert_PASS(check(ttFont, {'license_contents': good_license}),
                'with a good OFL.txt license with "https://" url.')


    # modify a tiny bit of the license text, to trigger the FAIL:
    bad_license = check["license_contents"].replace("SIL OPEN FONT LICENSE Version 1.1",
                                                    "SOMETHING ELSE :-P Version Foo")
    assert_results_contain(check(ttFont, {'license_contents': bad_license}),
                           FAIL, "incorrect-ofl-body-text",
                           "with incorrect ofl body text")


def test_check_name_license(mada_ttFonts):
    """ Check copyright namerecords match license file. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/license")

    # Our reference Mada family has its copyright name records properly set
    # identifying it as being licensed under the Open Font License
    for ttFont in mada_ttFonts:
        assert_PASS(check(ttFont),
                    'with good fonts ...')

    for ttFont in mada_ttFonts:
        assert_results_contain(check(ttFont, {"license": "LICENSE.txt"}), # Apache
                               FAIL, 'wrong',
                               'with wrong entry values ...')

    for ttFont in mada_ttFonts:
        delete_name_table_id(ttFont, NameID.LICENSE_DESCRIPTION)
        assert_results_contain(check(ttFont),
                               FAIL, 'missing',
                               'with missing copyright namerecords ...')

    # TODO:
    # WARN, "http" / "http-in-description"


def NOT_IMPLEMENTED_test_check_name_license_url():
    """ License URL matches License text on name table? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/name/license_url")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, code="ufl"
    # - FAIL, code="licensing-inconsistency"
    # - FAIL, code="no-license-found"
    # - FAIL, code="bad-entries"
    # - WARN, code="http-in-description"
    # - WARN, code="http"
    # - PASS


def test_check_name_description_max_length():
    """ Description strings in the name table
        must not exceed 200 characters.
    """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/description_max_length")

    # Our reference Mada Regular is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # Here we add strings to NameID.DESCRIPTION with exactly 100 chars,
    # so it should still PASS:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.DESCRIPTION:
            ttFont['name'].names[i].string = ('a' * 200).encode(name.getEncoding())
    assert_PASS(check(ttFont),
                'with a 200 char string...')

    # And here we make the strings longer than 200 chars
    # in order to make the check emit a WARN:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.DESCRIPTION:
            ttFont['name'].names[i].string = ('a' * 201).encode(name.getEncoding())
    assert_results_contain(check(ttFont),
                           WARN, 'too-long',
                           'with a too long description string...')


def test_check_hinting_impact():
    """ Show hinting filesize impact. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/hinting_impact")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(check(font),
                           INFO, 'size-impact',
                           'this check always emits an INFO result...')
    # TODO: test the CFF code-path


def test_check_file_size():
    """Ensure files are not too large."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/file_size")

    assert_PASS(check(TEST_FILE("mada/Mada-Regular.ttf")))

    assert_results_contain(check(TEST_FILE("varfont/inter/Inter[slnt,wght].ttf")),
                           WARN, 'large-font',
                           'with quite a big font...')

    assert_results_contain(check(TEST_FILE("cjk/SourceHanSans-Regular.otf")),
                           FAIL, 'massive-font',
                           'with a very big font...')

def test_check_name_version_format():
    """ Version format is correct in 'name' table ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/version_format")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # then we introduce bad strings in all version-string entries:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.VERSION_STRING:
            invalid = "invalid-version-string".encode(name.getEncoding())
            ttFont["name"].names[i].string = invalid
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-version-strings',
                           'with bad version format in name table...')

    # and finally we remove all version-string entries:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.VERSION_STRING:
            del ttFont["name"].names[i]
    assert_results_contain(check(ttFont),
                           FAIL, 'no-version-string',
                           'with font lacking version string entries in name table...')


def NOT_IMPLEMENTED_test_check_old_ttfautohint():
    """ Font has old ttfautohint applied? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/old_ttfautohint")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, code="lacks-version-strings"
    # - INFO, code="version-not-detected"  "Could not detect which version of ttfautohint
    #                                       was used in this font."
    # - WARN, code="old-ttfa"  "detected an old ttfa version"
    # - PASS
    # - FAIL, code="parse-error"


@pytest.mark.parametrize("expected_status,expected_keyword,reason,font",[
    (FAIL, "lacks-ttfa-params",
     'with a font lacking ttfautohint params on its version strings on the name table.',
     TEST_FILE("coveredbyyourgrace/CoveredByYourGrace.ttf")),

    (SKIP, "not-hinted",
     'with a font which appears to our heuristic as not hinted using ttfautohint.',
     TEST_FILE("mada/Mada-Regular.ttf")),

    (PASS, "ok",
     'with a font that has ttfautohint params'
     ' (-l 6 -r 36 -G 0 -x 10 -H 350 -D latn -f cyrl -w "" -X "")',
     TEST_FILE("merriweather/Merriweather-Regular.ttf"))
])
def test_check_has_ttfautohint_params(expected_status, expected_keyword, reason, font):
    """ Font has ttfautohint params? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/has_ttfautohint_params")

    assert_results_contain(check(font),
                           expected_status, expected_keyword,
                           reason)


def test_check_epar():
    """ EPAR table present in font? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/epar")

    # Our reference Mada Regular lacks an EPAR table:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must emit an INFO message inviting the designers
    # to learn more about it:
    assert_results_contain(check(ttFont),
                           INFO, 'lacks-EPAR',
                           'with a font lacking an EPAR table...')

    # add a fake EPAR table to validate the PASS code-path:
    ttFont["EPAR"] = "foo"
    assert_PASS(check(ttFont),
                'with a good font...')


def NOT_IMPLEMENTED_test_check_gasp():
    """ Is GASP table correctly set? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/gasp")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "lacks-gasp"        "Font is missing the gasp table."
    # - FAIL, "empty"             "The gasp table has no values."
    # - FAIL, "lacks-ffff-range"  "The gasp table does not have a 0xFFFF gasp range."
    # - INFO, "ranges"            "These are the ppm ranges declared on the gasp table:"
    # - WARN, "non-ffff-range"    "The gasp table has a range that may be unneccessary."
    # - WARN, "unset-flags"       "All flags in gasp range 0xFFFF (i.e. all font sizes) must be set to 1"
    # - PASS                      "The gasp table is correctly set."


def test_check_name_familyname_first_char():
    """ Make sure family name does not begin with a digit. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/familyname_first_char")

    # Our reference Mada Regular is known to be good
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # alter the family-name prepending a digit:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            ttFont["name"].names[i].string = "1badname".encode(name.getEncoding())

    # and make sure the check FAILs:
    assert_results_contain(check(ttFont),
                           FAIL, 'begins-with-digit',
                           'with a font in which the family name begins with a digit...')


def test_check_name_ascii_only_entries():
    """ Are there non-ASCII characters in ASCII-only NAME table entries? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/ascii_only_entries")

    # Our reference Merriweather Regular is known to be good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    #  The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).
    #  For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that
    #  string should be the same in CFF fonts which also have this
    #  requirement in the OpenType spec.

    # Let's check detection of both. First nameId 6:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.POSTSCRIPT_NAME:
            ttFont['name'].names[i].string = "Infração".encode(encoding="utf-8")

    assert_results_contain(check(ttFont),
                           FAIL, 'bad-string',
                           'with non-ascii on nameID 6 entry (Postscript name)...')

    assert_results_contain(check(ttFont),
                           FAIL, 'non-ascii-strings',
                           'with non-ascii on nameID 6 entry (Postscript name)...')

    # Then reload the good font
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # And check detection of a problem on nameId 0:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont['name'].names[i].string = "Infração".encode(encoding="utf-8")

    assert_results_contain(check(ttFont),
                           FAIL, 'bad-string',
                           'with non-ascii on nameID 0 entry (Copyright notice)...')

    assert_results_contain(check(ttFont),
                           FAIL, 'non-ascii-strings',
                           'with non-ascii on nameID 0 entry (Copyright notice)...')

    # Reload the good font once more:
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    #  Note:
    #  A common place where we find non-ASCII strings is on name table
    #  entries with NameID > 18, which are expressly for localising
    #  the ASCII-only IDs into Hindi / Arabic / etc.

    # Let's check a good case of a non-ascii on the name table then!
    # Choose an arbitrary name entry to mess up with:
    index = 5

    ttFont['name'].names[index].nameID = 19
    ttFont['name'].names[index].string = "Fantástico!".encode(encoding="utf-8")
    assert_PASS(check(ttFont),
                'with non-ascii on entries with nameId > 18...')


def test_split_camel_case_condition():
    from fontbakery.utils import split_camel_case
    assert split_camel_case("Lobster") == "Lobster"
    assert split_camel_case("LibreCaslonText") == "Libre Caslon Text"


def test_check_metadata_listed_on_gfonts():
    """ METADATA.pb: Fontfamily is listed on Google Fonts API? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/listed_on_gfonts")

    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    # Our reference FamilySans family is a just a generic example
    # and thus is not really hosted (nor will ever be hosted) at Google Fonts servers:
    assert_results_contain(check(font),
                           WARN, 'not-found',
                           f'with "{font}", from a family that\'s'
                           f' not listed on GFonts...')

    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    # Our reference Merriweather family is available on the Google Fonts collection:
    assert_PASS(check(font),
                f'with "{font}", from a family that is'
                f' listed on Google Fonts API...')

    font = TEST_FILE("abeezee/ABeeZee-Regular.ttf")
    # This is to ensure the code handles well camel-cased familynames.
    assert_PASS(check(font),
                f'with "{font}", listed and with a camel-cased name...')

    font = TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf")
    # And the check should also properly handle space-separated multi-word familynames.
    assert_PASS(check(font),
                f'with "{font}", available and with a space-separated family name...')


def test_check_metadata_unique_full_name_values():
    """ METADATA.pb: check if fonts field only has unique "full_name" values. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/unique_full_name_values")

    # Our reference FamilySans family is good:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font),
                'with a good family...')

    # then duplicate a full_name entry to make it FAIL:
    md = check["family_metadata"]
    md.fonts[0].full_name = md.fonts[1].full_name
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'duplicated',
                           'with a duplicated full_name entry.')


def test_check_metadata_unique_weight_style_pairs():
    """ METADATA.pb: check if fonts field only contains unique style:weight pairs. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/unique_weight_style_pairs")

    # Our reference FamilySans family is good:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font),
                'with a good family...')

    # then duplicate a pair of style & weight entries to make it FAIL:
    md = check["family_metadata"]
    md.fonts[0].style = md.fonts[1].style
    md.fonts[0].weight = md.fonts[1].weight
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'duplicated',
                           'with a duplicated pair of style & weight entries')


def test_check_metadata_license():
    """ METADATA.pb license is "APACHE2", "UFL" or "OFL"? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/license")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    good_licenses = ["APACHE2", "UFL", "OFL"]
    some_bad_values = ["APACHE", "Apache", "Ufl", "Ofl", "Open Font License"]

    check(font)
    md = check["family_metadata"]
    for good in good_licenses:
        md.license = good
        assert_PASS(check(font, {"family_metadata": md}),
                    f': {good}')

    for bad in some_bad_values:
        md.license = bad
        assert_results_contain(check(font, {"family_metadata": md}),
                               FAIL, 'bad-license',
                               f': {bad}')


def test_check_metadata_menu_and_latin():
    """ METADATA.pb should contain at least "menu" and "latin" subsets. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/menu_and_latin")

    # Let's start with our reference FamilySans family:
    fonts = TEST_FILE("familysans/FamilySans-Regular.ttf")

    good_cases = [
        ["menu", "latin"],
        ["menu", "cyrillic", "latin"],
    ]

    bad_cases = [
        ["menu"],
        ["latin"],
        [""],
        ["latin", "cyrillyc"],
        ["khmer"]
    ]

    check(fonts)
    md = check["family_metadata"]
    for good in good_cases:
        del md.subsets[:]
        md.subsets.extend(good)
        assert_PASS(check(fonts, {"family_metadata": md}),
                    f'with subsets = {good}')

    for bad in bad_cases:
        del md.subsets[:]
        md.subsets.extend(bad)
        assert_results_contain(check(fonts, {"family_metadata": md}),
                               FAIL, 'missing',
                               f'with subsets = {bad}')


def test_check_metadata_subsets_order():
    """ METADATA.pb subsets should be alphabetically ordered. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/subsets_order")

    # Let's start with our reference FamilySans family:
    fonts = TEST_FILE("familysans/FamilySans-Regular.ttf")

    good_cases = [
        ["latin", "menu"],
        ["cyrillic", "latin", "menu"],
        ["cyrillic", "khmer", "latin", "menu"],
    ]

    bad_cases = [
        ["menu", "latin"],
        ["latin", "cyrillic", "menu"],
        ["cyrillic", "menu", "khmer", "latin"],
    ]

    check(fonts)
    md = check["family_metadata"]
    for good in good_cases:
        del md.subsets[:]
        md.subsets.extend(good)
        assert_PASS(check(fonts, {"family_metadata": md}),
                    f'with subsets = {good}')

    md = check["family_metadata"]
    for bad in bad_cases:
        del md.subsets[:]
        md.subsets.extend(bad)
        assert_results_contain(check(fonts, {"family_metadata": md}),
                               FAIL, 'not-sorted',
                               f'with subsets = {bad}')


def test_check_metadata_includes_production_subsets():
    """Check METADATA.pb has production subsets."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/includes_production_subsets")

    # We need to use a family that is already in production
    # Our reference Cabin is known to be good
    fonts = cabin_fonts

    # So it must PASS the check:
    assert_PASS(check(fonts),
                "with a good METADATA.pb for this family...")

    # Then we induce the problem by removing a subset:
    md = check["family_metadata"]
    md.subsets.pop()
    assert_results_contain(check(fonts, {"family_metadata": md}),
                           FAIL, 'missing-subsets',
                           'with a bad METADATA.pb (last subset has been removed)...')


def test_check_metadata_copyright():
    """ METADATA.pb: Copyright notice is the same in all fonts? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/copyright")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know its copyright notices are consistent:
    assert_PASS(check(font),
                'with consistent copyright notices on FamilySans...')

    # Now we make them diverge:
    md = check["family_metadata"]
    md.fonts[1].copyright = md.fonts[0].copyright + " arbitrary suffix!" # to make it different

    # To ensure the problem is detected:
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'inconsistency',
                           'with diverging copyright notice strings...')


def test_check_metadata_familyname():
    """ Check that METADATA.pb family values are all the same. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/familyname")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know its family name entries on METADATA.pb are consistent:
    assert_PASS(check(font),
                'with consistent family name...')

    # Now we make them diverge:
    md = check["family_metadata"]
    md.fonts[1].name = md.fonts[0].name + " arbitrary suffix!" # to make it different

    # To ensure the problem is detected:
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'inconsistency',
                           'With diverging Family name metadata entries...')


def test_check_metadata_has_regular():
    """ METADATA.pb: According Google Fonts standards, families should have a Regular style. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/has_regular")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans has got a regular declares in its METADATA.pb file:
    assert_PASS(check(font),
                'with Family Sans, a family with a regular style...')

    # We remove the regular:
    md = check["family_metadata"]
    for i in range(len(md.fonts)):
        if md.fonts[i].filename == "FamilySans-Regular.ttf":
            del md.fonts[i]
            break

    # and make sure the check now FAILs:
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'lacks-regular',
                           'with a METADATA.pb file without a regular...')


def test_check_metadata_regular_is_400():
    """ METADATA.pb: Regular should be 400. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/regular_is_400")

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans' Regular has a weight value equal to 400, so the check should PASS:
    assert_PASS(check(font),
                'with Family Sans, a family with regular=400...')

    md = check["family_metadata"]
    # The we change the value for its regular:
    for i in range(len(md.fonts)):
        if md.fonts[i].filename == "FamilySans-Regular.ttf":
            md.fonts[i].weight = 500

    # and make sure the check now FAILs:
    assert_results_contain(check(font, {"family_metadata": md}),
                           FAIL, 'not-400',
                           'with METADATA.pb with regular=500...')


def test_check_metadata_nameid_family_name():
    """ Checks METADATA.pb font.name field matches
        family name declared on the name table. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/nameid/family_name")

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans Regular is good here:
    assert_PASS(check(font))

    # Then cause it to fail:
    md = check["font_metadata"]
    md.name = "Foo"
    assert_results_contain(check(font, {"font_metadata": md}),
                           FAIL, "mismatch")

    # TODO: the failure-mode below seems more generic than the scope
    #       of this individual check. This could become a check by itself!
    #
    # code-paths:
    # - FAIL code="missing", "Font lacks a FONT_FAMILY_NAME entry"


def test_check_metadata_nameid_post_script_name():
    """ Checks METADATA.pb font.post_script_name matches
        postscript name declared on the name table. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/nameid/post_script_name")

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans Regular is good here:
    assert_PASS(check(font))

    # Then cause it to fail:
    md = check["font_metadata"]
    md.post_script_name = "Foo"
    assert_results_contain(check(font, {'font_metadata': md}),
                           FAIL, 'mismatch')

    # TODO: the failure-mode below seems more generic than the scope
    #       of this individual check. This could become a check by itself!
    #
    # code-paths:
    # - FAIL code="missing", "Font lacks a POSTSCRIPT_NAME"


def test_check_metadata_nameid_full_name():
    """ METADATA.pb font.fullname value matches fullname declared on the name table ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/nameid/full_name")

    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")

    assert_PASS(check(font),
                'with a good font...')

    # here we change the font.fullname on the METADATA.pb
    # to introduce a "mismatch" error condition:
    font_metadata = check['font_metadata']
    good = font_metadata.full_name
    font_metadata.full_name = good + "bad-suffix"

    assert_results_contain(check(font, {"font_metadata": font_metadata}),
                           FAIL, 'mismatch',
                           'with mismatching fullname values...')

    # and restore the good value prior to the next test case:
    font_metadata.full_name = good

    # And here we remove all FULL_FONT_NAME entries
    # in order to get a "lacks-entry" error condition:
    ttFont = check['ttFont']
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            del ttFont["name"].names[i]
    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-entry',
                           'when a font lacks FULL_FONT_NAME entries in its name table...')


def test_check_metadata_nameid_font_name():
    """ METADATA.pb font.name value should be same as the family name declared on the name table. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/nameid/font_name")

    # Our reference Merriweather-Regular is know to have good fullname metadata
    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont),
                'with a good font...')

    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            good = name.string.decode(name.getEncoding()) # keep a copy of the good value
            ttFont["name"].names[i].string = (good + "bad-suffix").encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'mismatch',
                                   f'with a bad FULL_FONT_NAME entry ({i})...')
            ttFont["name"].names[i].string = good # restore good value

    # TODO:
    # FAIL, "lacks-entry"


def test_check_metadata_match_fullname_postscript():
    """ METADATA.pb family.full_name and family.post_script_name
        fields have equivalent values ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/match_fullname_postscript")

    regular_font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    lightitalic_font = TEST_FILE("merriweather/Merriweather-LightItalic.ttf")

    assert_PASS(check(lightitalic_font),
                'with good entries (Merriweather-LightItalic)...')
    #            post_script_name: "Merriweather-LightItalic"
    #            full_name:        "Merriweather Light Italic"

    # TODO: Verify why/whether "Regular" cannot be omited on font.full_name
    #       There's some relevant info at:
    #       https://github.com/googlefonts/fontbakery/issues/1517
    #
    # FIXME: com.google.fonts/check/metadata/nameid/full_name
    #        ties the full_name values from the METADATA.pb file and the
    #        internal name table entry (FULL_FONT_NAME)
    #        to be strictly identical. So it seems that the test below is
    #        actually wrong (as well as the current implementation):
    #
    assert_results_contain(check(regular_font),
                           FAIL, 'mismatch',
                           'with bad entries (Merriweather-Regular)...')
    #                       post_script_name: "Merriweather-Regular"
    #                       full_name:        "Merriweather"

    # fix the regular metadata:
    md = check['font_metadata']
    md.full_name = "Merriweather Regular"

    assert_PASS(check(regular_font, {"font_metadata": md}),
                'with good entries (Merriweather-Regular after full_name fix)...')
    #            post_script_name: "Merriweather-Regular"
    #            full_name:        "Merriweather Regular"


    # introduce an error in the metadata:
    md.full_name = "MistakenFont Regular"

    assert_results_contain(check(regular_font, {"font_metadata": md}),
                           FAIL, 'mismatch',
                           'with a mismatch...')
    #                       post_script_name: "Merriweather-Regular"
    #                       full_name:        "MistakenFont Regular"


def NOT_IMPLEMENTED_test_check_match_filename_postscript():
    """ METADATA.pb family.filename and family.post_script_name
        fields have equivalent values? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/match_filename_postscript")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "mismatch"		"METADATA.pb filename does not match post_script_name"
    # - PASS


MONTSERRAT_RIBBI = [
    TEST_FILE("montserrat/Montserrat-Regular.ttf"),
    TEST_FILE("montserrat/Montserrat-Italic.ttf"),
    TEST_FILE("montserrat/Montserrat-Bold.ttf"),
    TEST_FILE("montserrat/Montserrat-BoldItalic.ttf")
]
MONTSERRAT_NON_RIBBI = [
    TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Black.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
    TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Light.ttf"),
    TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Medium.ttf"),
    TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),
    TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
    TEST_FILE("montserrat/Montserrat-Thin.ttf")
]

def test_check_metadata_valid_name_values():
    """ METADATA.pb font.name field contains font name in right format? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/valid_name_values")

    # Our reference Montserrat family is a good 18-styles family:
    for font in MONTSERRAT_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(font),
                    f'with a good RIBBI font ({font})...')

        # And fail if it finds a bad font_familyname:
        assert_results_contain(check(font, {"font_familynames": ["WrongFamilyName"]}),
                               FAIL, 'mismatch',
                               f'with a bad RIBBI font ({font})...')

    # We do the same for NON-RIBBI styles:
    for font in MONTSERRAT_NON_RIBBI:

        # So it must PASS the check:
        assert_PASS(check(font),
                    'with a good NON-RIBBI font ({fontfile})...')

        # And fail if it finds a bad font_familyname:
        assert_results_contain(check(font, {"typographic_familynames": ["WrongFamilyName"]}),
                               FAIL, 'mismatch',
                               f'with a bad NON-RIBBI font ({font})...')


def test_check_metadata_valid_full_name_values():
    """ METADATA.pb font.full_name field contains font name in right format? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/valid_full_name_values")

    # Our reference Montserrat family is a good 18-styles family:
    # properly described in its METADATA.pb file:
    for font in MONTSERRAT_RIBBI:

        # So it must PASS the check:
        assert_PASS(check(font),
                    'with a good RIBBI font ({fontfile})...')

        # And fail if the full familyname in METADATA.pb diverges
        # from the name inferred from the name table:
        assert_results_contain(check(font, {"font_familynames": ["WrongFamilyName"]}),
                               FAIL, 'mismatch',
                               f'with a bad RIBBI font ({font})...')

    # We do the same for NON-RIBBI styles:
    for font in MONTSERRAT_NON_RIBBI:

        # So it must PASS the check:
        assert_PASS(check(font),
                    f'with a good NON-RIBBI font ({font})...')

        # Unless when not matching typographic familyname from the name table:
        assert_results_contain(check(font, {"typographic_familynames": ["WrongFamilyName"]}),
                               FAIL, 'mismatch',
                               f'with a bad NON-RIBBI font ({font})...')


def test_check_metadata_valid_filename_values():
    """ METADATA.pb font.filename field contains font name in right format? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/valid_filename_values")

    # Our reference Montserrat family is a good 18-styles family:
    for font in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(font),
                    f"with a good font ({font})...")

        # And fail if it finds a bad filename:
        meta = check["family_metadata"]
        for i in range(len(meta.fonts)):
            meta.fonts[i].filename = "WrongFileName"
        assert_results_contain(check(font, {"family_metadata": meta}),
                               FAIL, 'bad-field',
                               f'with bad filename metadata ("WrongFileName")'
                               f' for fontfile "{font}"...')


def test_check_metadata_valid_post_script_name_values():
    """ METADATA.pb font.post_script_name field contains font name in right format? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/valid_post_script_name_values")

    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(fontfile),
                    f"with a good font ({fontfile})...")

        # And fail if it finds a bad filename:
        md = check["font_metadata"]
        md.post_script_name = "WrongPSName"
        assert_results_contain(check(fontfile, {"font_metadata": md}),
                               FAIL, 'mismatch',
                               f'with a bad font ({fontfile})...')


def test_check_metadata_valid_copyright():
    """ Copyright notice on METADATA.pb matches canonical pattern ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/valid_copyright")

    # Our reference Cabin Regular is known to be bad
    # Since it provides an email instead of a git URL:
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, 'bad-notice-format',
                           'with a bad copyright notice string...')

    # Then we change it into a good string (example extracted from Archivo Black):
    # note: the check does not actually verify that the project name is correct.
    #       It only focuses on the string format.
    good_string = ("Copyright 2017 The Archivo Black Project Authors"
                   " (https://github.com/Omnibus-Type/ArchivoBlack)")
    md = check["font_metadata"]
    md.copyright = good_string
    assert_PASS(check(font, {"font_metadata": md}),
                'with a good copyright notice string...')

    # We also ignore case, so these should also PASS:
    md.copyright = good_string.upper()
    assert_PASS(check(font, {"font_metadata": md}),
                'with all uppercase...')

    md.copyright = good_string.lower()
    assert_PASS(check(font, {"font_metadata": md}),
                'with all lowercase...')


def test_check_font_copyright():
    """Copyright notices match canonical pattern in fonts"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/font_copyright")

    # Our reference Cabin Regular is known to be bad
    # Since it provides an email instead of a git URL:
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-notice-format',
                           'with a bad copyright notice string...')

    # We change it into a good string (example extracted from Archivo Black):
    # note: the check does not actually verify that the project name is correct.
    #       It only focuses on the string format.
    good_string = ("Copyright 2017 The Archivo Black Project Authors"
                   " (https://github.com/Omnibus-Type/ArchivoBlack)")
    for i, entry in enumerate(ttFont['name'].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont['name'].names[i].string = good_string.encode(entry.getEncoding())
    assert_PASS(check(ttFont),
                'with good strings...')


def DISABLE_test_check_glyphs_file_font_copyright():
    """Copyright notices match canonical pattern in fonts"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/glyphs_file/font_copyright")

    glyphsFile = GLYPHSAPP_TEST_FILE("Comfortaa.glyphs")
    # note: the check does not actually verify that the project name is correct.
    #       It only focuses on the string format.

    # Use an email instead of a git URL:
    bad_string = ("Copyright 2017 The Archivo Black Project Authors"
                  " (contact-us@fake-address.com)")
    glyphsFile.copyright = bad_string
    assert_results_contain(check(glyphsFile),
                           FAIL, 'bad-notice-format',
                           'with a bad copyright notice string...')

    # We change it into a good string (example extracted from Archivo Black):
    good_string = ("Copyright 2017 The Archivo Black Project Authors"
                   " (https://github.com/Omnibus-Type/ArchivoBlack)")
    glyphsFile.copyright = good_string
    assert_PASS(check(glyphsFile),
                'with a good coopyright string...')


def test_check_metadata_reserved_font_name():
    """ Copyright notice on METADATA.pb should not contain Reserved Font Name. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/reserved_font_name")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                'with a good copyright notice string...')

    # Then we make it bad:
    md = check["font_metadata"]
    md.copyright += "Reserved Font Name"
    assert_results_contain(check(font, {"font_metadata": md}),
                           WARN, 'rfn',
                           'with a notice containing "Reserved Font Name"...')


def test_check_metadata_copyright_max_length():
    """ METADATA.pb: Copyright notice shouldn't exceed 500 chars. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/copyright_max_length")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    check(font)
    md = check["font_metadata"]

    md.copyright = 500 * "x"
    assert_PASS(check(font, {"font_metadata": md}),
                'with a 500-char copyright notice string...')

    md.copyright = 501 * "x"
    assert_results_contain(check(font, {"font_metadata": md}),
                           FAIL, 'max-length',
                           'with a 501-char copyright notice string...')


def test_check_metadata_filenames():
    """ METADATA.pb: Font filenames match font.filename entries? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/filenames")

    assert_PASS(check(montserrat_fonts),
                'with matching list of font files...')

    # make sure missing files are detected by the check:
    fonts = montserrat_fonts
    original_name = fonts[0]
    # rename one font file in order to trigger the FAIL
    os.rename(original_name, "font.tmp")
    assert_results_contain(check(fonts),
                           FAIL, 'file-not-found',
                           'with missing font files...')
    os.rename("font.tmp", original_name) # restore filename


    # From all TTFs in Cabin's directory, the condensed ones are not
    # listed on METADATA.pb, so the check must FAIL, even if we do not
    # explicitely include them in the set of files to be checked:
    assert_results_contain(check(cabin_fonts),
                           FAIL, 'file-not-declared',
                           'with some font files not declared...')


def test_check_metadata_italic_style():
    """ METADATA.pb font.style "italic" matches font internals ? """
    from fontbakery.constants import MacStyle
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/italic_style")

    # Our reference Merriweather Italic is known to good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Italic.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # now let's introduce issues on the FULL_FONT_NAME entries
    # to test the "bad-fullfont-name" codepath:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "BAD VALUE".encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'bad-fullfont-name',
                                   'with a bad NameID.FULL_FONT_NAME entry...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup

    # And, finally, let's flip off that italic bit
    # and get a "bad-macstyle" FAIL (so much fun!):
    ttFont['head'].macStyle &= ~MacStyle.ITALIC
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-macstyle',
                           'with bad macstyle bit value...')


def test_check_metadata_normal_style():
    """ METADATA.pb font.style "normal" matches font internals ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/normal_style")
    from fontbakery.constants import MacStyle

    # This one is pretty similar to check/metadata/italic_style
    # You may want to take a quick look above...

    # Our reference Merriweather Regular is known to be good here.
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # now we sadically insert brokenness into
    # each occurrence of the FONT_FAMILY_NAME nameid:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "Merriweather-Italic".encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'familyname-italic',
                                   'with a non-italic font that has a "-Italic" in FONT_FAMILY_NAME...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup

    # now let's do the same with
    # occurrences of the FULL_FONT_NAME nameid:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "Merriweather-Italic".encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'fullfont-italic',
                                   'with a non-italic font that has a "-Italic" in FULL_FONT_NAME...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup

    # And, finally, again, we flip a bit and...
    #
    # Note: This time the boolean logic is the quite opposite in comparison
    # to the test for com.google.fonts/check/metadata/italic_style above.
    # Here we have to set the bit back to 1 to get a wrongful "this font is an italic" setting:
    ttFont['head'].macStyle |= MacStyle.ITALIC
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-macstyle',
                           'with bad macstyle bit value...')


def test_check_metadata_nameid_family_and_full_names():
    """ METADATA.pb font.name and font.full_name fields match the values declared on the name table? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/nameid/family_and_full_names")

    # Our reference Merriweather Regular is known to be good here.
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # There we go again!
    # Breaking FULL_FONT_NAME entries one by one:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "This is utterly wrong!".encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'fullname-mismatch',
                                   'with a METADATA.pb / FULL_FONT_NAME mismatch...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup

    # And then we do the same with FONT_FAMILY_NAME entries:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            backup = name.string
            ttFont['name'].names[i].string = ("I'm listening to"
                                              " The Players with Hiromasa Suzuki - Galaxy (1979)").encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'familyname-mismatch',
                                   'with a METADATA.pb / FONT_FAMILY_NAME mismatch...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup


def test_check_metadata_fontname_not_camel_cased():
    """ METADATA.pb: Check if fontname is not camel cased. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/fontname_not_camel_cased")

    # Our reference Cabin Regular is known to be good
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                'with a good font...')

    # Then we FAIL with a CamelCased name:
    md = check["font_metadata"]
    md.name = "GollyGhost"
    assert_results_contain(check(font, {"font_metadata": md}),
                           FAIL, 'camelcase',
                           'with a bad font name (CamelCased)...')

    # And we also make sure the check PASSes with a few known good names:
    for good_name in ["VT323",
                      "PT Sans",
                      "Amatic SC"]:
        md.name = good_name
        assert_PASS(check(font, {"font_metadata": md}),
                    f'with a good font name "{good_name}"...')


def test_check_metadata_match_name_familyname():
    """ METADATA.pb: Check font name is the same as family name. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/match_name_familyname")

    # Our reference Cabin Regular is known to be good
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                'with a good font...')

    # Then we FAIL with mismatching names:
    family_md = check["family_metadata"]
    font_md = check["font_metadata"]
    family_md.name = "Some Fontname"
    font_md.name = "Something Else"
    assert_results_contain(check(font, {"family_metadata": family_md,
                                        "font_metadata": font_md}),
                           FAIL, 'mismatch',
                           'with bad font/family name metadata...')


def test_check_check_metadata_canonical_weight_value():
    """ METADATA.pb: Check that font weight has a canonical value. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/canonical_weight_value")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    check(font)
    md = check["font_metadata"]

    for w in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
        md.weight = w
        assert_PASS(check(font, {"font_metadata": md}),
                    f'with a good weight value ({w})...')

    for w in [150, 250, 350, 450, 550, 650, 750, 850]:
        md.weight = w
        assert_results_contain(check(font, {"font_metadata": md}),
                               FAIL, 'bad-weight',
                               'with a bad weight value ({w})...')


def test_check_metadata_os2_weightclass():
    """ Checking OS/2 usWeightClass matches weight specified at METADATA.pb """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/os2_weightclass")

    # === test cases for Variable Fonts ===
    # Our reference Jura is known to be good
    ttFont = TTFont(TEST_FILE("varfont/jura/Jura[wght].ttf"))
    assert_PASS(check(ttFont),
                f'with a good metadata...')

    # Should report if a bad weight value is ifound though:
    md = check["font_metadata"]
    good_value = md.weight
    bad_value = good_value + 100
    md.weight = bad_value
    assert_results_contain(check(ttFont, {"font_metadata": md}),
                           FAIL, 'mismatch',
                           f'with a bad metadata...')

    ttFont = TTFont(TEST_FILE("leaguegothic-vf/LeagueGothic[wdth].ttf"))
    assert_PASS(check(ttFont),
                f'with a good VF that lacks a "wght" axis....')
                # See: https://github.com/googlefonts/fontbakery/issues/3529

    # === test cases for Static Fonts ===
    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        ttFont = TTFont(fontfile)
        assert_PASS(check(ttFont),
                    f'with a good font ({fontfile})...')

        # but should report bad weight values:
        md = check["font_metadata"]
        good_value = md.weight
        bad_value = good_value + 50
        md.weight = bad_value
        assert_results_contain(check(ttFont, {"font_metadata": md}),
                               FAIL, 'mismatch',
                               f'with bad metadata for {fontfile}...')

        # If font is Thin or ExtraLight, ensure that this check can
        # accept both 100, 250 for Thin and 200, 275 for ExtraLight
        if "Thin" in fontfile:
            ttFont["OS/2"].usWeightClass = 100
            assert_PASS(check(ttFont),
                        f'with weightclass 100 on ({fontfile})...')

            ttFont["OS/2"].usWeightClass = 250
            assert_PASS(check(ttFont),
                        f'with weightclass 250 on ({fontfile})...')

        if "ExtraLight" in fontfile:
            ttFont["OS/2"].usWeightClass = 200
            assert_PASS(check(ttFont),
                        f'with weightClass 200 on ({fontfile})...')

            ttFont["OS/2"].usWeightClass = 275
            assert_PASS(check(ttFont),
                        f'with weightClass 275 on ({fontfile})...')


def NOT_IMPLEMENTED_test_check_metadata_match_weight_postscript():
    """ METADATA.pb: Metadata weight matches postScriptName. """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/metadata/match_weight_postscript")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "METADATA.pb: Font weight value is invalid."
    # - FAIL, "METADATA.pb: Mismatch between postScriptName and weight value."
    # - PASS


def NOT_IMPLEMENTED_test_check_metadata_canonical_style_names():
    """ METADATA.pb: Font styles are named canonically? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/metadata/canonical_style_names")
    # TODO: Implement-me!
    #
    # code-paths:
    # - SKIP		"Applicable only to font styles declared as 'italic' or 'normal' on METADATA.pb."
    # - FAIL, "italic"	"Font style should be italic."
    # - FAIL, "normal"	"Font style should be normal."
    # - PASS		"Font styles are named canonically."


def test_check_unitsperem_strict():
    """ Stricter unitsPerEm criteria for Google Fonts. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/unitsperem_strict")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    PASS_VALUES = [16, 32, 64, 128, 256, 512, 1024] # Good for better performance on legacy renderers
    PASS_VALUES.extend([500, 1000]) # or common typical values
    PASS_VALUES.extend([2000, 2048]) # not so common, but still ok

    WARN_LARGE_VALUES = [2500, 4000, 4096] # uncommon and large,
                                           # but we've seen legitimate cases such as the
                                           # Big Shoulders Family which uses 4000 since
                                           # it needs more details.

    # and finally the bad ones, including:
    FAIL_VALUES = [0, 1, 2, 4, 8, 15, 16385] # simply invalid
    FAIL_VALUES.extend([100, 1500, 5000]) # suboptimal (uncommon and not power of two)
    FAIL_VALUES.extend([8192, 16384]) # and valid ones suggested by the opentype spec,
                                      # but too large, causing undesireable filesize bloat.


    for pass_value in PASS_VALUES:
        ttFont["head"].unitsPerEm = pass_value
        assert_PASS(check(ttFont),
                    f'with unitsPerEm = {pass_value}...')


    for warn_value in WARN_LARGE_VALUES:
        ttFont["head"].unitsPerEm = warn_value
        assert_results_contain(check(ttFont),
                               WARN, 'large-value',
                               f'with unitsPerEm = {warn_value}...')

    for fail_value in FAIL_VALUES:
        ttFont["head"].unitsPerEm = fail_value
        assert_results_contain(check(ttFont),
                               FAIL, 'bad-value',
                               f'with unitsPerEm = {fail_value}...')


def NOT_IMPLEMENTED_test_check_version_bump():
    """ Version number has increased since previous release on Google Fonts? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/version_bump")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "Version number is equal to version on Google Fonts."
    # - FAIL, "Version number is less than version on Google Fonts."
    # - FAIL, "Version number is equal to version on Google Fonts GitHub repo."
    # - FAIL, "Version number is less than version on Google Fonts GitHub repo."
    # - PASS


def NOT_IMPLEMENTED_test_check_production_glyphs_similarity():
    """ Glyphs are similiar to Google Fonts version? """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/production_glyphs_similarity")
    # TODO: Implement-me!
    #
    # code-paths:
    # - WARN, "Following glyphs differ greatly from Google Fonts version"
    # - PASS, "Glyphs are similar"


def NOT_IMPLEMENTED_test_check_fsselection():
    """ Checking OS/2 fsSelection value. """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/fsselection")
    # TODO: Implement-me!
    #
    # code-paths:
    # ...


def test_check_italic_angle():
    """ Checking post.italicAngle value. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/italic_angle")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # italic-angle, style, fail_message
    test_cases = [
        [1, "Italic", FAIL, "positive"],
        [0, "Regular", PASS, None], # This must PASS as it is a non-italic
        [-21, "ThinItalic", WARN, "over-minus20-degrees"],
        [-30, "ThinItalic", WARN, "over-minus20-degrees"],
        [-31, "ThinItalic", FAIL, "over-minus30-degrees"],
        [0, "Italic", FAIL, "zero-italic"],
        [-1,"ExtraBold", FAIL, "non-zero-normal"]
    ]

    for value, style, expected_result, expected_msg in test_cases:
        ttFont["post"].italicAngle = value

        if expected_result != PASS:
            assert_results_contain(check(ttFont, {"style": style}),
                                   expected_result,
                                   expected_msg,
                                   f"with italic-angle:{value} style:{style}...")
        else:
            assert_PASS(check(ttFont, {"style": style}),
                        f'with italic-angle:{value} style:{style}...')


def test_check_mac_style():
    """ Checking head.macStyle value. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/mac_style")
    from fontbakery.constants import MacStyle

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # macStyle-value, style, expected
    test_cases = [
        [0, "Thin", PASS],
        [0, "Bold", "bad-BOLD"],
        [0, "Italic", "bad-ITALIC"],
        [MacStyle.ITALIC, "Italic", PASS],
        [MacStyle.ITALIC, "Thin", "bad-ITALIC"],
        [MacStyle.BOLD, "Bold", PASS],
        [MacStyle.BOLD, "Thin", "bad-BOLD"],
        [MacStyle.BOLD | MacStyle.ITALIC, "BoldItalic", PASS]
    ]

    for macStyle_value, style, expected in test_cases:
        ttFont["head"].macStyle = macStyle_value

        if expected == PASS:
            assert_PASS(check(ttFont, {"style": style}),
                        'with macStyle:{macStyle_value} style:{style}...')
        else:
            assert_results_contain(check(ttFont, {"style": style}),
                                   FAIL, expected,
                                   f"with macStyle:{macStyle_value} style:{style}...")


# FIXME!
# GFonts hosted Cabin files seem to have changed in ways
# that break some of the assumptions in the code-test below.
# More info at https://github.com/googlefonts/fontbakery/issues/2581
@pytest.mark.xfail(strict=True)
def test_check_production_encoded_glyphs(cabin_ttFonts):
    """Check glyphs are not missing when compared to version on fonts.google.com"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/production_encoded_glyphs")

    for font in cabin_fonts:
        # Cabin font hosted on fonts.google.com contains
        # all the glyphs for the font in data/test/cabin
        assert_PASS(check(font),
                    f"with '{font}'")

        ttFont = check["ttFont"]
        # Take A glyph out of font
        ttFont['cmap'].getcmap(3, 1).cmap.pop(ord('A'))
        ttFont['glyf'].glyphs.pop('A')
        assert_results_contain(check(ttFont),
                               FAIL, 'lost-glyphs')


def test_check_metadata_nameid_copyright():
    """ Copyright field for this font on METADATA.pb matches
        all copyright notice entries on the name table? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/nameid/copyright")
    from fontbakery.utils import get_name_entry_strings

    # Our reference Cabin Regular is known to be good
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                "with a good METADATA.pb for this font...")

    # But the check must report when mismatching names are found:
    good_value = get_name_entry_strings(check["ttFont"],
                                        NameID.COPYRIGHT_NOTICE)[0]
    md = check["font_metadata"]
    md.copyright = good_value + "something bad"
    assert_results_contain(check(font, {"font_metadata": md}),
                           FAIL, 'mismatch',
                           'with a bad METADATA.pb'
                           ' (with a copyright string not matching this font)...')


def test_check_metadata_category():
    """ Category field for this font on METADATA.pb is valid? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/category")

    # Our reference Cabin family...
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    check(font)
    md = check["family_metadata"]
    assert md.category == "SANS_SERIF" # ...is known to be good ;-)
    assert_PASS(check(font),
                "with a good METADATA.pb...")

    # We then report a problem with this sample of bad values:
    for bad_value in ["SAN_SERIF",
                      "MONO_SPACE",
                      "sans_serif",
                      "monospace"]:
        md.category = bad_value
        assert_results_contain(check(font, {"family_metadata": md}),
                               FAIL, 'bad-value',
                               f'with a bad category "{bad_value}"...')

    # And we accept the good ones:
    for good_value in ["MONOSPACE",
                       "SANS_SERIF",
                       "SERIF",
                       "DISPLAY",
                       "HANDWRITING"]:
        md.category = good_value
        assert_PASS(check(font, {"family_metadata": md}),
                    f'with "{good_value}"...')


def test_check_name_mandatory_entries():
    """ Font has all mandatory 'name' table entries ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/mandatory_entries")

    # We'll check both RIBBI and non-RIBBI fonts
    # so that we cover both cases for FAIL/PASS scenarios

    # === First with a RIBBI font: ===
    # Our reference Cabin Regular is known to be good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont),
                "with a good RIBBI font...")

    mandatory_entries = [NameID.FONT_FAMILY_NAME,
                         NameID.FONT_SUBFAMILY_NAME,
                         NameID.FULL_FONT_NAME,
                         NameID.POSTSCRIPT_NAME]

    # then we "remove" each mandatory entry one by one:
    for mandatory in mandatory_entries:
        ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
        for i, name in enumerate(ttFont['name'].names):
            if name.nameID == mandatory:
                ttFont['name'].names[i].nameID = 0 # not really removing it, but replacing it
                                                   # by something else completely irrelevant
                                                   # for the purposes of this specific check
        assert_results_contain(check(ttFont),
                               FAIL, 'missing-entry',
                               f'with a missing madatory (RIBBI) name entry (id={mandatory})...')

    # === And now a non-RIBBI font: ===
    # Our reference Merriweather Black is known to be good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Black.ttf"))
    assert_PASS(check(ttFont),
                "with a good non-RIBBI font...")

    mandatory_entries = [NameID.FONT_FAMILY_NAME,
                         NameID.FONT_SUBFAMILY_NAME,
                         NameID.FULL_FONT_NAME,
                         NameID.POSTSCRIPT_NAME,
                         NameID.TYPOGRAPHIC_FAMILY_NAME,
                         NameID.TYPOGRAPHIC_SUBFAMILY_NAME]

    # then we (again) "remove" each mandatory entry one by one:
    for mandatory in mandatory_entries:
        ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Black.ttf"))
        for i, name in enumerate(ttFont['name'].names):
            if name.nameID in mandatory_entries:
                ttFont['name'].names[i].nameID = 0 # not really removing it, but replacing it
                                                   # by something else completely irrelevant
                                                   # for the purposes of this specific check
        assert_results_contain(check(ttFont),
                               FAIL, 'missing-entry',
                               'with a missing madatory (non-RIBBI) name entry (id={mandatory})...')


def test_condition_familyname_with_spaces():
    from fontbakery.profiles.googlefonts_conditions import familyname_with_spaces
    assert familyname_with_spaces("OverpassMono") == "Overpass Mono"
    assert familyname_with_spaces("BodoniModa11") == "Bodoni Moda 11"


def test_check_name_familyname():
    """ Check name table: FONT_FAMILY_NAME entries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/familyname")

    # TODO: FAIL, "lacks-name"

    test_cases = [
        #expect                      filename                                      mac_value        win_value
        (PASS, "ok",       TEST_FILE("cabin/Cabin-Regular.ttf"),                   "Cabin",         "Cabin"),
        (FAIL, "mismatch", TEST_FILE("cabin/Cabin-Regular.ttf"),                   "Wrong",         "Cabin"),
        (PASS, "ok",       TEST_FILE("overpassmono/OverpassMono-Regular.ttf"),     "Overpass Mono", "Overpass Mono"),
        (PASS, "ok",       TEST_FILE("overpassmono/OverpassMono-Bold.ttf"),        "Overpass Mono", "Overpass Mono"),
        (FAIL, "mismatch", TEST_FILE("overpassmono/OverpassMono-Regular.ttf"),     "Overpass Mono", "Foo"),
        (PASS, "ok",       TEST_FILE("merriweather/Merriweather-Black.ttf"),       "Merriweather",  "Merriweather Black"),
        (PASS, "ok",       TEST_FILE("merriweather/Merriweather-LightItalic.ttf"), "Merriweather",  "Merriweather Light"),
        (FAIL, "mismatch", TEST_FILE("merriweather/Merriweather-LightItalic.ttf"), "Merriweather",  "Merriweather Light Italic"),
        (PASS, "ok",       TEST_FILE("abeezee/ABeeZee-Regular.ttf"), "ABeeZee",  "ABeeZee"),
        # Note: ABeeZee is a good camel-cased name exception.
    ]

    for expected, keyword, filename, mac_value, win_value in test_cases:
        ttFont = TTFont(filename)
        for i, name in enumerate(ttFont['name'].names):
            if name.platformID == PlatformID.MACINTOSH:
                value = mac_value
            if name.platformID == PlatformID.WINDOWS:
                value = win_value
            assert value

            if name.nameID == NameID.FONT_FAMILY_NAME:
                ttFont['name'].names[i].string = value.encode(name.getEncoding())
        assert_results_contain(check(ttFont),
                                     expected, keyword,
                                     f'with filename="{filename}",'
                                     f' value="{value}", style="{check["style"]}"...')


def test_check_name_subfamilyname():
    """ Check name table: FONT_SUBFAMILY_NAME entries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/subfamilyname")

    PASS_test_cases = [
        #          filename                                       mac_value             win_value
        (TEST_FILE("overpassmono/OverpassMono-Regular.ttf"),      "Regular",            "Regular"),
        (TEST_FILE("overpassmono/OverpassMono-Bold.ttf"),         "Bold",               "Bold"),
        (TEST_FILE("merriweather/Merriweather-Black.ttf"),        "Black",              "Regular"),
        (TEST_FILE("merriweather/Merriweather-LightItalic.ttf"),  "Light Italic",       "Italic"),
        (TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"),      "Black Italic",       "Italic"),
        (TEST_FILE("montserrat/Montserrat-Black.ttf"),            "Black",              "Regular"),
        (TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),       "Bold Italic",        "Bold Italic"),
        (TEST_FILE("montserrat/Montserrat-Bold.ttf"),             "Bold",               "Bold"),
        (TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"),  "ExtraBold Italic",   "Italic"),
        (TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"),        "ExtraBold",          "Regular"),
        (TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"), "ExtraLight Italic",  "Italic"),
        (TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),       "ExtraLight",         "Regular"),
        (TEST_FILE("montserrat/Montserrat-Italic.ttf"),           "Italic",             "Italic"),
        (TEST_FILE("montserrat/Montserrat-LightItalic.ttf"),      "Light Italic",       "Italic"),
        (TEST_FILE("montserrat/Montserrat-Light.ttf"),            "Light",              "Regular"),
        (TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"),     "Medium Italic",      "Italic"),
        (TEST_FILE("montserrat/Montserrat-Medium.ttf"),           "Medium",             "Regular"),
        (TEST_FILE("montserrat/Montserrat-Regular.ttf"),          "Regular",            "Regular"),
        (TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"),   "SemiBold Italic",    "Italic"),
        (TEST_FILE("montserrat/Montserrat-SemiBold.ttf"),         "SemiBold",           "Regular"),
        (TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),       "Thin Italic",        "Italic"),
        (TEST_FILE("montserrat/Montserrat-Thin.ttf"),             "Thin",               "Regular")
    ]

    for filename, mac_value, win_value in PASS_test_cases:
        ttFont = TTFont(filename)
        for i, name in enumerate(ttFont['name'].names):
            if name.platformID == PlatformID.MACINTOSH:
                value = mac_value
            if name.platformID == PlatformID.WINDOWS:
                value = win_value
            assert value

            if name.nameID == NameID.FONT_SUBFAMILY_NAME:
                ttFont['name'].names[i].string = value.encode(name.getEncoding())

        results = check(ttFont)
        style = check["expected_style"]
        assert_PASS(results,
                    f"with filename='{filename}', value='{value}', "
                    f"style_win='{style.win_style_name}', "
                    f"style_mac='{style.mac_style_name}'...")

    # - FAIL, "bad-familyname" - "Bad familyname value on a FONT_SUBFAMILY_NAME entry."
    filename = TEST_FILE("montserrat/Montserrat-ThinItalic.ttf")
    ttFont = TTFont(filename)
    # We setup a bad entry:
    ttFont["name"].setName("Not a proper style",
                           NameID.FONT_SUBFAMILY_NAME,
                           PlatformID.MACINTOSH,
                           MacintoshEncodingID.ROMAN,
                           MacintoshLanguageID.ENGLISH)

    # And this should now FAIL:
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-familyname')

    # Repeat this for a Win subfamily name
    ttFont = TTFont(filename)
    ttFont["name"].setName("Not a proper style",
                           NameID.FONT_SUBFAMILY_NAME,
                           PlatformID.WINDOWS,
                           WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-familyname')


def test_check_name_fullfontname():
    """ Check name table: FULL_FONT_NAME entries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/fullfontname")

    # Our reference Cabin Regular is known to be good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont),
                "with a good Regular font...")

    # Let's now test the Regular exception
    # ('Regular' can be optionally ommited on the FULL_FONT_NAME entry):
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont["name"].names[index].string = "Cabin".encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   WARN, 'lacks-regular',
                                   'with a good Regular font that omits "Regular" on FULL_FONT_NAME...')
            # restore it:
            ttFont["name"].names[index].string = backup

    # Let's also make sure our good reference Cabin BoldItalic PASSes the check.
    # This also tests the splitting of filename infered style with a space char
    ttFont = TTFont(TEST_FILE("cabin/Cabin-BoldItalic.ttf"))
    assert_PASS(check(ttFont),
                "with a good Bold Italic font...")

    # And here we test the FAIL codepath:
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont["name"].names[index].string = "MAKE IT FAIL".encode(name.getEncoding())
            assert_results_contain(check(ttFont),
                                   FAIL, 'bad-entry',
                                   'with a bad FULL_FONT_NAME entry...')
            # restore it:
            ttFont["name"].names[index].string = backup

    # And we should also accept a few camel-cased familyname exceptions,
    # so this one should also be fine:
    ttFont = TTFont(TEST_FILE("abeezee/ABeeZee-Regular.ttf"))
    assert_PASS(check(ttFont),
                "with a good camel-cased fontname...")


def NOT_IMPLEMENTED_test_check_name_postscriptname():
    """ Check name table: POSTSCRIPT_NAME entries. """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/name/postscriptname")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "bad-entry"
    # - PASS


def test_check_name_typographicfamilyname():
    """ Check name table: TYPOGRAPHIC_FAMILY_NAME entries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/typographicfamilyname")

    # RIBBI fonts must not have a TYPOGRAPHIC_FAMILY_NAME entry
    ttFont = TTFont(TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"))
    assert_PASS(check(ttFont),
                f"with a RIBBI without nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...")

    # so we add one and make sure the check reports the problem:
    ttFont['name'].names[5].nameID = NameID.TYPOGRAPHIC_FAMILY_NAME # 5 is arbitrary here
    assert_results_contain(check(ttFont),
                           FAIL, 'ribbi',
                           f'with a RIBBI that has got a nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...')

    # non-RIBBI fonts must have a TYPOGRAPHIC_FAMILY_NAME entry
    ttFont = TTFont(TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"))
    assert_PASS(check(ttFont),
                f"with a non-RIBBI containing a nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...")

    # set bad values on all TYPOGRAPHIC_FAMILY_NAME entries:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
            ttFont['name'].names[i].string = "foo".encode(name.getEncoding())

    assert_results_contain(check(ttFont),
                           FAIL, 'non-ribbi-bad-value',
                           'with a non-RIBBI with bad nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entries...')

    # remove all TYPOGRAPHIC_FAMILY_NAME entries
    # by changing their nameid to something else:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
            ttFont['name'].names[i].nameID = 255 # blah! :-)

    assert_results_contain(check(ttFont),
                           FAIL, 'non-ribbi-lacks-entry',
                           f'with a non-RIBBI lacking a nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...')


def test_check_name_typographicsubfamilyname():
    """ Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/typographicsubfamilyname")

    RIBBI = "montserrat/Montserrat-BoldItalic.ttf"
    NON_RIBBI = "montserrat/Montserrat-ExtraLight.ttf"

    # Add incorrect TYPOGRAPHIC_SUBFAMILY_NAME entries to a RIBBI font
    ttFont = TTFont(TEST_FILE(RIBBI))
    ttFont['name'].setName("FOO",
                           NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                           PlatformID.WINDOWS,
                           WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    ttFont['name'].setName("BAR",
                           NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                           PlatformID.MACINTOSH,
                           MacintoshEncodingID.ROMAN,
                           MacintoshLanguageID.ENGLISH)
    assert_results_contain(check(ttFont),
                           FAIL, 'mismatch',
                           f'with a RIBBI that has got incorrect'
                           f' nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entries...')
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-win-name')
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-mac-name')

    # non-RIBBI fonts must have a TYPOGRAPHIC_SUBFAMILY_NAME entry
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    assert_PASS(check(ttFont),
                f'with a non-RIBBI containing a nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entry...')

    # set bad values on the win TYPOGRAPHIC_SUBFAMILY_NAME entry:
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    ttFont['name'].setName("Generic subfamily name",
                           NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                           PlatformID.WINDOWS,
                           WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-typo-win',
                           f'with a non-RIBBI with bad nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entries...')

    # set bad values on the mac TYPOGRAPHIC_SUBFAMILY_NAME entry:
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    ttFont['name'].setName("Generic subfamily name",
                           NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                           PlatformID.MACINTOSH,
                           MacintoshEncodingID.ROMAN,
                           MacintoshLanguageID.ENGLISH)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-typo-mac',
                           f'with a non-RIBBI with bad nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entries...')


    # remove all TYPOGRAPHIC_SUBFAMILY_NAME entries
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    win_name = ttFont['name'].getName(NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                                      PlatformID.WINDOWS,
                                      WindowsEncodingID.UNICODE_BMP,
                                      WindowsLanguageID.ENGLISH_USA)
    mac_name = ttFont['name'].getName(NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                                      PlatformID.MACINTOSH,
                                      MacintoshEncodingID.ROMAN,
                                      MacintoshLanguageID.ENGLISH)
    win_name.nameID = 254
    if mac_name:
        mac_name.nameID = 255
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-typo-win',
                           f'with a non-RIBBI lacking a nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entry...')
                           # note: the check must not complain
                           #       about the lack of a mac entry!


def test_check_name_copyright_length():
    """ Length of copyright notice must not exceed 500 characters. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/name/copyright_length")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    good_entry = 'a' * 499
    for i, entry in enumerate(ttFont['name'].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont['name'].names[i].string = good_entry.encode(entry.getEncoding())
    assert_PASS(check(ttFont),
                'with 499-byte copyright notice string...')

    good_entry = 'a' * 500
    for i, entry in enumerate(ttFont['name'].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont['name'].names[i].string = good_entry.encode(entry.getEncoding())
    assert_PASS(check(ttFont),
                'with 500-byte copyright notice string...')

    bad_entry = 'a' * 501
    for i, entry in enumerate(ttFont['name'].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont['name'].names[i].string = bad_entry.encode(entry.getEncoding())
    assert_results_contain(check(ttFont),
                           FAIL, 'too-long',
                           'with 501-byte copyright notice string...')


# TODO: Maybe skip this code-test if the service is offline?
# we could use pytest.mak.skipif here together with a piece of code that
# verifies whether or not the namecheck.fontdata.com website is online at the moment
def test_check_fontdata_namecheck():
    """ Familyname is unique according to namecheck.fontdata.com """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/fontdata_namecheck")

    TIMEOUT_MSG = ("Sometimes namecheck.fontdata.com times out"
                   " and we don't want to stop running all the other"
                   " code tests. Unless you touched this portion of"
                   " the code, it is generaly safe to ignore this glitch.")
    # We dont FAIL because this is meant as a merely informative check
    # There may be frequent cases when fonts are being updated and thus
    # already have a public family name registered on the
    # namecheck.fontdata.com database.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font),
                           INFO, 'name-collision',
                           'with an already used name...',
                           ignore_error=TIMEOUT_MSG)

    # Here we know that FamilySans has not been (and will not be)
    # registered as a real family.
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font),
                'with a unique family name...',
                ignore_error=TIMEOUT_MSG)


def test_check_fontv():
    """ Check for font-v versioning """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/fontv")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           INFO, 'bad-format',
                           'with a font that does not follow'
                           ' the suggested font-v versioning scheme ...')

    from fontv.libfv import FontVersion
    fv = FontVersion(ttFont)
    fv.set_state_git_commit_sha1(development=True)
    version_string = fv.get_name_id5_version_string()
    for record in ttFont['name'].names:
        if record.nameID == NameID.VERSION_STRING:
            record.string = version_string
    assert_PASS(check(ttFont),
                'with one that follows the suggested scheme ...')


def test_check_glyf_nested_components():
    """Check glyphs do not have nested components."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/glyf_nested_components")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # We need to create a nested component. "second" has components, so setting
    # one of "quotedbl"'s components to "second" should do it.
    ttFont['glyf']['quotedbl'].components[0].glyphName = "second"

    assert_results_contain(check(ttFont),
                           FAIL, 'found-nested-components')


# Temporarily disabling this code-test since check/negative_advance_width itself
# is disabled waiting for an implementation targetting the
# actual root cause of the issue.
#
# See also comments at googlefons.py as well as at
# https://github.com/googlefonts/fontbakery/issues/1727
def disabled_test_check_negative_advance_width():
    """ Check that advance widths cannot be inferred as negative. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/negative_advance_width")

    # Our reference Cabin Regular is good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # So it must PASS
    assert_PASS(check(ttFont),
                'with a good font...')

    # We then change values in an arbitrary glyph
    # in the glyf table in order to cause the problem:
    glyphName = "J"
    coords = ttFont["glyf"].glyphs[glyphName].coordinates

# FIXME:
# Note: I thought this was the proper way to induce the
# issue, but now I think I'll need to look more
# carefully at sample files providedby MarcFoley
# to see what's really at play here and how the relevant
# data is encoded into the affected OpenType files.
    rightSideX = coords[-3][0]
    # leftSideX: (make right minus left a negative number)
    coords[-4][0] = rightSideX + 1

    ttFont["glyf"].glyphs[glyphName].coordinates = coords

    # and now this should FAIL:
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-coordinates',
                           'with bad coordinates on the glyf table...')


def test_check_varfont_generate_static():
    """ Check a static ttf can be generated from a variable font. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont/generate_static")

    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))
    assert_PASS(check(ttFont))

    # Removing a table to deliberately break variable font
    del ttFont['fvar']
    assert_results_contain(check(ttFont),
                           FAIL, 'varlib-mutator')


def test_check_varfont_has_HVAR():
    """ Check that variable fonts have an HVAR table. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont/has_HVAR")

    # Our reference Cabin Variable Font contains an HVAR table.
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))

    # So the check must PASS.
    assert_PASS(check(ttFont))

    # Introduce the problem by removing the HVAR table:
    del ttFont['HVAR']
    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-HVAR')


def test_check_smart_dropout():
    """ Font enables smart dropout control in "prep" table instructions? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/smart_dropout")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))

    # "Program at 'prep' table contains
    #  instructions enabling smart dropout control."
    assert_PASS(check(ttFont))

    # "Font does not contain TrueType instructions enabling
    #  smart dropout control in the 'prep' table program."
    import array
    ttFont["prep"].program.bytecode = array.array('B', [0])
    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-smart-dropout')


def test_check_vttclean():
    """ There must not be VTT Talk sources in the font. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/vttclean")

    good_font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(good_font))

    bad_font = TEST_FILE("hinting/Roboto-VF.ttf")
    assert_results_contain(check(bad_font),
                           FAIL, 'has-vtt-sources')


def test_check_aat():
    """ Are there unwanted Apple tables ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/aat")

    unwanted_tables = [
        'EBSC', 'Zaph', 'acnt', 'ankr', 'bdat', 'bhed', 'bloc',
        'bmap', 'bsln', 'fdsc', 'feat', 'fond', 'gcid', 'just',
        'kerx', 'lcar', 'ltag', 'mort', 'morx', 'opbd', 'prop',
        'trak', 'xref'
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
                               FAIL, 'has-unwanted-tables',
                               f'with unwanted table {unwanted} ...')


def test_check_fvar_name_entries():
    """ All name entries referenced by fvar instances exist on the name table? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/fvar_name_entries")

    # This broken version of the Expletus variable font, was where this kind of problem was first observed:
    ttFont = TTFont(TEST_FILE("broken_expletus_vf/ExpletusSansBeta-VF.ttf"))

    # So it must FAIL the check:
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-name',
                           'with a bad font...')

    # If we add the name entry with id=265 (which was the one missing)
    # then the check must now PASS:
    from fontTools.ttLib.tables._n_a_m_e import makeName
    ttFont["name"].names.append(makeName("Foo", 265, 1, 0, 0))

    assert_PASS(check(ttFont),
                'with a good font...')


def test_check_varfont_has_instances():
    """ A variable font must have named instances. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont_has_instances")

    # ExpletusVF does have instances.
    # Note: The "broken" in the path name refers to something else.
    #       (See test_check_fvar_name_entries)
    ttFont = TTFont(TEST_FILE("broken_expletus_vf/ExpletusSansBeta-VF.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont),
                'with a good font...')

    # If we delete all instances, then it must FAIL:
    while len(ttFont["fvar"].instances):
        del ttFont["fvar"].instances[0]

    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-named-instances',
                           'with a bad font...')


def test_check_varfont_weight_instances():
    """ Variable font weight coordinates must be multiples of 100. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont_weight_instances")

    # This copy of Markazi Text has an instance with
    # a 491 'wght' coordinate instead of 500.
    ttFont = TTFont(TEST_FILE("broken_markazitext/MarkaziText-VF.ttf"))

    # So it must FAIL the check:
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-coordinate',
                           'with a bad font...')

    # Let's then change the weight coordinates to make it PASS the check:
    for i, instance in enumerate(ttFont["fvar"].instances):
        ttFont["fvar"].instances[i].coordinates['wght'] -= instance.coordinates['wght'] % 100

    assert_PASS(check(ttFont),
                'with a good font...')


def NOT_IMPLEMENTED_test_check_family_tnum_horizontal_metrics():
    """ All tabular figures must have the same width across the RIBBI-family. """
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/family/tnum_horizontal_metrics")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "inconsistent-widths"
    # - PASS


def test_check_integer_ppem_if_hinted():
    """ PPEM must be an integer on hinted fonts. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/integer_ppem_if_hinted")

    # Our reference Merriweather Regular is hinted, but does not set
    # the "rounded PPEM" flag (bit 3 on the head table flags) as
    # described at https://docs.microsoft.com/en-us/typography/opentype/spec/head
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # So it must FAIL the check:
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-flags',
                           'with a bad font...')

    # hotfixing it should make it PASS:
    ttFont["head"].flags |= (1 << 3)

    assert_PASS(check(ttFont),
                'with a good font...')


def test_check_ligature_carets():
    """ Is there a caret position declared for every ligature? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/ligature_carets")

    # Our reference Mada Medium is known to be bad
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    assert_results_contain(check(ttFont),
                           WARN, 'lacks-caret-pos',
                           'with a bad font...')

    # And FamilySans Regular is also bad
    ttFont = TTFont("data/test/familysans/FamilySans-Regular.ttf")
    assert_results_contain(check(ttFont),
                           WARN, 'GDEF-missing',
                           'with a bad font...')

    # TODO: test the following code-paths:
    # - WARN "incomplete-caret-pos-data"
    # - FAIL "malformed"
    # - PASS (We currently lack a reference family that PASSes this check!)


def test_check_kerning_for_non_ligated_sequences():
    """ Is there kerning info for non-ligated sequences ? """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/kerning_for_non_ligated_sequences")

    # Our reference Mada Medium is known to be good
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')

    # And Merriweather Regular is known to be bad
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           WARN, 'lacks-kern-info',
                           'with a bad font...')


def test_check_family_control_chars():
    """Are any unacceptable control characters present in font files?"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/family/control_chars")

    good_font = TEST_FILE("bad_character_set/control_chars/"
                          "FontbakeryTesterCCGood-Regular.ttf")
    onebad_cc_font = TEST_FILE("bad_character_set/control_chars/"
                               "FontbakeryTesterCCOneBad-Regular.ttf")
    multibad_cc_font = TEST_FILE("bad_character_set/control_chars/"
                                 "FontbakeryTesterCCMultiBad-Regular.ttf")

    # No unacceptable control characters should pass with one file
    fonts = [good_font]
    assert_PASS(check(fonts),
                'with one good font...')

    # No unacceptable control characters should pass with multiple good files
    fonts = [good_font,
             good_font]
    assert_PASS(check(fonts),
                'with multiple good fonts...')

    # Unacceptable control chars should fail with one file x one bad char in font
    fonts = [onebad_cc_font]
    assert_results_contain(check(fonts),
                           FAIL, 'unacceptable',
                           'with one bad font that has one bad char...')

    # Unacceptable control chars should fail with one file x multiple bad char in font
    fonts = [multibad_cc_font]
    assert_results_contain(check(fonts),
                           FAIL, 'unacceptable',
                           'with one bad font that has multiple bad char...')

    # Unacceptable control chars should fail with multiple files x multiple bad chars in fonts
    fonts = [onebad_cc_font,
             multibad_cc_font]
    assert_results_contain(check(fonts),
                           FAIL, 'unacceptable',
                           'with multiple bad fonts that have multiple bad chars...')


def test_check_family_italics_have_roman_counterparts():
    """Ensure Italic styles have Roman counterparts."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/family/italics_have_roman_counterparts")

    # The path used here, "some-crazy.path/", is meant to ensure
    # that the parsing code does not get lost when trying to
    # extract the style of a font file.
    fonts = ['some-crazy.path/merriweather/Merriweather-BlackItalic.ttf',
             'some-crazy.path/merriweather/Merriweather-Black.ttf',
             'some-crazy.path/merriweather/Merriweather-BoldItalic.ttf',
             'some-crazy.path/merriweather/Merriweather-Bold.ttf',
             'some-crazy.path/merriweather/Merriweather-Italic.ttf',
             'some-crazy.path/merriweather/Merriweather-LightItalic.ttf',
             'some-crazy.path/merriweather/Merriweather-Light.ttf',
             'some-crazy.path/merriweather/Merriweather-Regular.ttf']

    assert_PASS(check(fonts),
                'with a good family...')

    fonts.pop(-1) # remove the last one, which is the Regular
    assert 'some-crazy.path/merriweather/Merriweather-Regular.ttf' not in fonts
    assert 'some-crazy.path/merriweather/Merriweather-Italic.ttf' in fonts
    assert_results_contain(check(fonts),
                           FAIL, 'missing-roman',
                           'with a family that has an Italic but lacks a Regular.')

    fonts.append('some-crazy.path/merriweather/MerriweatherItalic.ttf')
    assert_results_contain(check(fonts),
                           WARN, 'bad-filename',
                           'with a family that has a non-canonical italic filename.')

    # This check must also be able to deal with variable fonts!
    fonts = ["cabinvfbeta/CabinVFBeta-Italic[wdth,wght].ttf",
             "cabinvfbeta/CabinVFBeta[wdth,wght].ttf"]
    assert_PASS(check(fonts),
                'with a good set of varfonts...')

    fonts = ["cabinvfbeta/CabinVFBeta-Italic[wdth,wght].ttf"]
    assert_results_contain(check(fonts),
                           FAIL, 'missing-roman',
                           'with an Italic varfont that lacks a Roman counterpart.')


def NOT_IMPLEMENTED__test_com_google_fonts_check_repo_dirname_match_nameid_1():
    """Are any unacceptable control characters present in font files?"""
    # check = CheckTester(googlefonts_profile,
    #                     "com.google.fonts/check/repo_dirname_match_nameid_1")
    # TODO: Implement-me!
    #
    # PASS
    # FAIL, "lacks-regular"
    # FAIL, "mismatch"
    #
    #  passing_file = TEST_FILE(".../.ttf")
    #  fonts = [passing_file]
    #  assert_PASS(check(fonts),
    #              'with one good font...')


def test_check_repo_vf_has_static_fonts():
    """Check VF family dirs in google/fonts contain static fonts"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/repo/vf_has_static_fonts")
    import tempfile
    import shutil
    # in order for this check to work, we need to
    # mimic the folder structure of the Google Fonts repository
    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        family_dir = portable_path(tmp_gf_dir + "/ofl/testfamily")
        src_family = portable_path("data/test/varfont")
        shutil.copytree(src_family, family_dir)

        assert_results_contain(check([], {"family_directory": family_dir}),
                               WARN, 'missing',
                               'for a VF family which does not has a static dir.')

        static_dir = portable_path(family_dir + "/static")
        os.mkdir(static_dir)
        assert_results_contain(check([], {"family_directory": family_dir}),
                               FAIL, 'empty',
                               'for a VF family which has a static dir'
                               ' but no fonts in the static dir.')

        static_fonts = portable_path("data/test/cabin")
        shutil.rmtree(static_dir)
        shutil.copytree(static_fonts, static_dir)
        assert_PASS(check([], {"family_directory": family_dir}),
                    'for a VF family which has a static dir and static fonts')


def test_check_repo_upstream_yaml_has_required_fields():
    """Check upstream.yaml has all required fields"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/repo/upstream_yaml_has_required_fields")
    upstream_yaml = {
        "branch": "main",
        "files": {"TestFamily-Regular.ttf": "TestFamily-Regular.ttf"}
    }
    # Pass if upstream.yaml file contains all fields
    assert_PASS(check([], {"upstream_yaml": upstream_yaml}),
                'for an upstream.yaml which contains all fields')

    # Fail if it doesn't
    upstream_yaml.pop("files")
    assert_results_contain(check([], {"upstream_yaml": upstream_yaml}),
                           FAIL, "missing-fields",
                           "for an upsream.yaml which doesn't contain all fields")


def test_check_repo_fb_report():
    """ A font repository should not include fontbakery report files """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/repo/fb_report")
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmp_dir:
        family_dir = portable_path(tmp_dir)
        src_family = portable_path("data/test/varfont")
        shutil.copytree(src_family, family_dir)

        assert_PASS(check([], {"family_directory": family_dir}),
                    'for a repo without Font Bakery report files.')

        assert_PASS(check([], {"family_directory": family_dir}),
                    'with a json file that is not a Font Bakery report.')

        # Add a json file that is not a FB report
        open(os.path.join(family_dir,
                          "something_else.json"), "w+").write("this is not a FB report")

        FB_REPORT_SNIPPET = """
{
    "result": {
        "INFO": 8,
        "PASS": 81,
        "SKIP": 74,
        "WARN": 4
    },
    "sections": [
    """
        # Report files must be detected even if placed on subdirectories
        # and the check code shuld not rely only on filename (such as "Jura-Regular.fb-report.json")
        # but should instead inspect the contents of the file:
        open(os.path.join(family_dir,
                          "jura",
                          "static",
                          "my_fontfamily_name.json"), "w+").write(FB_REPORT_SNIPPET)
        assert_results_contain(check([], {"family_directory": family_dir}),
                               WARN, 'fb-report',
                               'with an actual snippet of a report.')


def test_check_repo_zip_files():
    """ A font repository should not include ZIP files """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/repo/zip_files")
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmp_dir:
        family_dir = portable_path(tmp_dir)
        src_family = portable_path("data/test/varfont")
        shutil.copytree(src_family, family_dir)

        assert_PASS(check([], {"family_directory": family_dir}),
                    'for a repo without ZIP files.')

        for ext in ["zip", "rar", "7z"]:
            # ZIP files must be detected even if placed on subdirectories:
            filepath = os.path.join(family_dir,
                                    f"jura",
                                    f"static",
                                    f"fonts-release.{ext}")
            #create an empty file. The check won't care about the contents:
            open(filepath, "w+")
            assert_results_contain(check([], {"family_directory": family_dir}),
                                   FAIL, 'zip-files',
                                   f"when a {ext} file is found.")
            # remove the file before testing the next one ;-)
            os.remove(filepath)


def test_check_vertical_metrics_regressions(cabin_ttFonts):
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/vertical_metrics_regressions")
    from fontbakery.profiles.shared_conditions import family_directory

    ttFonts = [TTFont(f) for f in cabin_fonts]

    # Cabin test family should match by default
    assert_PASS(check(ttFonts),
                'with a good family...')

    # FAIL with changed vertical metric values
    local_regular = check["regular_ttFont"]
    local_regular['OS/2'].sTypoAscender = 0
    assert_results_contain(check(ttFonts, {"regular_ttFont": local_regular}),
                           FAIL, 'bad-typo-ascender',
                           'with a family which has an incorrect typoAscender...')

    local_regular['OS/2'].sTypoDescender = 0
    assert_results_contain(check(ttFonts, {"regular_ttFont": local_regular}),
                           FAIL, 'bad-typo-descender',
                           'with a family which has an incorrect typoDescender...')

    local_regular['hhea'].ascent = 0
    assert_results_contain(check(ttFonts, {"regular_ttFont": local_regular}),
                           FAIL, 'bad-hhea-ascender',
                           'with a family which has an incorrect hhea ascender...')

    local_regular['hhea'].descent = 0
    assert_results_contain(check(ttFonts, {"regular_ttFont": local_regular}),
                           FAIL, 'bad-hhea-descender',
                           'with a family which has an incorrect hhea descender...')

    # Fail if family on Google Fonts has fsSelection bit 7 enabled but checked fonts don't
    local_regular["OS/2"].fsSelection &= ~(1 << 7)
    assert_results_contain(check(ttFonts, {"regular_ttFont": local_regular}),
                           FAIL, "bad-fsselection-bit7",
                           "with a remote family which has typo metrics "
                           "enabled and the fonts being checked don't.")

    if 0: # FIXME:
        # Pass if family on Google Fonts doesn't have fsSelection bit 7 enabled
        # but checked fonts have taken this into consideration
        check(ttFonts)
        remote_regular = check["regular_remote_style"]
        local_regular = check["regular_ttFont"]

        remote_regular["OS/2"].fsSelection &= ~(1 << 7)
        local_regular["OS/2"].sTypoAscender = remote_regular["OS/2"].usWinAscent
        local_regular["OS/2"].sTypoDescender = -remote_regular["OS/2"].usWinDescent
        local_regular["hhea"].ascent = remote_regular["OS/2"].usWinAscent
        local_regular["hhea"].descent = -remote_regular["OS/2"].usWinDescent
        assert_PASS(check(ttFonts, {"regular_remote_style": remote_regular,
                                    "regular_ttFont": local_regular}),
                    'with a remote family which does not have typo metrics'
                    ' enabled but the checked fonts vertical metrics have been'
                    ' set so its typo and hhea metrics match the remote'
                    ' fonts win metrics.')

    if 0: # FIXME:
        # Same as previous check but using a remote font which has a different upm
        check(ttFonts)
        remote_regular = check["regular_remote_style"]
        local_regular = check["regular_ttFont"]

        remote_regular["OS/2"].fsSelection &= ~(1 << 7)
        remote_regular["head"].unitsPerEm = 2000
        # divide by 2 since we've doubled the upm
        local_regular["OS/2"].sTypoAscender = math.ceil(remote_regular["OS/2"].usWinAscent / 2)
        local_regular["OS/2"].sTypoDescender = math.ceil(-remote_regular["OS/2"].usWinDescent / 2)
        local_regular["hhea"].ascent = math.ceil(remote_regular["OS/2"].usWinAscent / 2)
        local_regular["hhea"].descent = math.ceil(-remote_regular["OS/2"].usWinDescent / 2)
        assert_PASS(check(ttFonts, {"regular_remote_style": remote_regular,
                                    "regular_ttFont": local_regular}),
                    'with a remote family which does not have typo metrics '
                    'enabled but the checked fonts vertical metrics have been '
                    'set so its typo and hhea metrics match the remote '
                    'fonts win metrics.')


    check(ttFonts)
    remote_regular = check["regular_remote_style"]
    local_regular = check["regular_ttFont"]
    local_regular['OS/2'].fsSelection &= ~(1 << 7)
    assert_results_contain(check(ttFonts, {"regular_remote_style": remote_regular,
                                           "regular_ttFont": local_regular}),
                           FAIL, "bad-fsselection-bit7",
                           'OS/2 fsSelection bit 7 must be enabled.')


    # Disable bit 7 in both fonts but change win metrics of ttFont
    check(ttFonts)
    remote_regular = check["regular_remote_style"]
    local_regular = check["regular_ttFont"]

    remote_regular["OS/2"].fsSelection &= ~(1 << 7)
    local_regular["OS/2"].fsSelection &= ~(1 << 7)
    local_regular["OS/2"].usWinAscent = 2500
    assert_results_contain(check(ttFonts, {"regular_remote_style": remote_regular,
                                           "regular_ttFont": local_regular}),
                           FAIL, "bad-fsselection-bit7",
                           'OS/2 fsSelection bit 7 must be enabled.')


def test_check_cjk_vertical_metrics():
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/cjk_vertical_metrics")

    ttFont = TTFont(cjk_font)
    assert_PASS(check(ttFont),
                'for Source Han Sans')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].fsSelection |= (1 << 7)
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-fselection-bit7',
                           'for font where OS/2 fsSelection bit 7 is enabled')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].sTypoAscender = float('inf')
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-OS/2.sTypoAscender',
                           'for font with bad OS/2.sTypoAscender')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].sTypoDescender = float('inf')
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-OS/2.sTypoDescender',
                           'for font with bad OS/2.sTypoDescender')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].sTypoLineGap = float('inf')
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-OS/2.sTypoLineGap',
                           'for font where linegaps have been set (OS/2 table)')

    ttFont = TTFont(cjk_font)
    ttFont['hhea'].lineGap = float('inf')
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-hhea.lineGap',
                           'for font where linegaps have been set (hhea table)')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].usWinAscent = float('inf')
    assert_results_contain(check(ttFont),
                           FAIL, 'ascent-mismatch',
                           'for a font where typo ascender != 0.88 * upm')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].usWinDescent = -float('inf')
    assert_results_contain(check(ttFont),
                           FAIL, 'descent-mismatch',
                           'for a font where typo descender != 0.12 * upm')

    ttFont = TTFont(cjk_font)
    ttFont['OS/2'].usWinAscent = float('inf')
    ttFont['hhea'].ascent = float('inf')
    assert_results_contain(check(ttFont),
                           WARN, 'bad-hhea-range',
                           'if font hhea and win metrics are greater than 1.5 * upm')


def test_check_cjk_vertical_metrics_regressions():
    # TODO: try to remove deepcopy usage
    from copy import deepcopy

    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/cjk_vertical_metrics_regressions")

    ttFont = TTFont(cjk_font)
    regular_remote_style = deepcopy(ttFont)

    # Check on duplicate
    regular_remote_style = deepcopy(ttFont)
    assert_PASS(check(ttFont, {"regular_remote_style": regular_remote_style}),
                'for Source Han Sans')

    # Change a single metric
    ttFont2 = deepcopy(ttFont)
    ttFont2['hhea'].ascent = 0
    assert_results_contain(check(ttFont2, {"regular_remote_style": regular_remote_style}),
                           FAIL, "cjk-metric-regression",
                           'hhea ascent is 0 when it should be 880')

    # Change upm of font being checked
    ttFont3 = deepcopy(ttFont)
    ttFont3['head'].unitsPerEm = 2000
    assert_results_contain(check(ttFont3, {"regular_remote_style": regular_remote_style}),
                           FAIL, "cjk-metric-regression",
                           'upm is 2000 and vert metrics values are not updated')

    # Change upm of checked font and update vert metrics
    ttFont4 = deepcopy(ttFont)
    ttFont4['head'].unitsPerEm = 2000
    for tbl, attrib in [("OS/2", "sTypoAscender"),
                        ("OS/2", "sTypoDescender"),
                        ("OS/2", "sTypoLineGap"),
                        ("OS/2", "usWinAscent"),
                        ("OS/2", "usWinDescent"),
                        ("hhea", "ascent"),
                        ("hhea", "descent"),
                        ("hhea", "lineGap")]:
        current_val = getattr(ttFont4[tbl], attrib)
        setattr(ttFont4[tbl], attrib, current_val * 2)
    assert_PASS(check(ttFont4, {"regular_remote_style": regular_remote_style}),
                'for Source Han Sans with doubled upm and doubled vert metrics')


def test_check_cjk_not_enough_glyphs():
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/cjk_not_enough_glyphs")
    ttFont = TTFont(cjk_font)
    assert_PASS(check(ttFont),
                'for Source Han Sans')

    ttFont = TTFont(TEST_FILE("montserrat/Montserrat-Regular.ttf"))
    assert_PASS(check(ttFont),
                'for Montserrat')

    # Let's modify Montserrat's cmap so there's a cjk glyph
    cmap = ttFont['cmap'].getcmap(3,1)
    # Add first character of the CJK unified Ideographs
    cmap.cmap[0x4E00] = "A"
    assert_results_contain(check(ttFont),
                           WARN, "cjk-not-enough-glyphs",
                           "There is only 1 CJK glyphs")
    # Add second character of the CJK unified Ideographs
    cmap.cmap[0x4E01] = "B"
    assert_results_contain(check(ttFont),
                           WARN, "cjk-not-enough-glyphs",
                           "There are only 2 CJK glyphs")


def test_check_varfont_instance_coordinates(vf_ttFont):
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont_instance_coordinates")

    # OpenSans-Roman-VF is correct
    assert_PASS(check(vf_ttFont),
                'with a variable font which has correct instance coordinates.')

    from copy import copy
    vf_ttFont2 = copy(vf_ttFont)
    for instance in vf_ttFont2['fvar'].instances:
        for axis in instance.coordinates.keys():
            instance.coordinates[axis] = 0
    assert_results_contain(check(vf_ttFont2),
                           FAIL, "bad-coordinate",
                           'with a variable font which does not have'
                           ' correct instance coordinates.')


def test_check_varfont_instance_names(vf_ttFont):
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont_instance_names")

    assert_PASS(check(vf_ttFont),
                'with a variable font which has correct instance names.')

    from copy import copy
    vf_ttFont2 = copy(vf_ttFont)
    for instance in vf_ttFont2['fvar'].instances:
        instance.subfamilyNameID = 300
    broken_name ="ExtraBlack Condensed 300pt"
    vf_ttFont2['name'].setName(broken_name,
                               300,
                               PlatformID.MACINTOSH,
                               MacintoshEncodingID.ROMAN,
                               MacintoshLanguageID.ENGLISH)
    vf_ttFont2['name'].setName(broken_name,
                               300,
                               PlatformID.WINDOWS,
                               WindowsEncodingID.UNICODE_BMP,
                               WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(vf_ttFont2),
                           FAIL, 'bad-instance-names',
                           'with a variable font which does not have correct instance names.')


def test_check_varfont_duplicate_instance_names(vf_ttFont):
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont_duplicate_instance_names")

    assert_PASS(check(vf_ttFont),
                'with a variable font which has unique instance names.')

    from copy import copy
    vf_ttFont2 = copy(vf_ttFont)
    duplicate_instance_name = vf_ttFont2['name'].getName(
        vf_ttFont2['fvar'].instances[0].subfamilyNameID,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA
    ).toUnicode()
    vf_ttFont2['name'].setName(string=duplicate_instance_name,
                               nameID=vf_ttFont2['fvar'].instances[1].subfamilyNameID,
                               platformID=PlatformID.WINDOWS,
                               platEncID=WindowsEncodingID.UNICODE_BMP,
                               langID=WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(vf_ttFont2),
                           FAIL, 'duplicate-instance-names')


def test_check_varfont_unsupported_axes():
    """Ensure VFs do not contain opsz or ital axes."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont/unsupported_axes")

    # Our reference varfont, CabinVFBeta.ttf, lacks 'ital' and 'slnt' variation axes.
    # So, should pass the check:
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))
    assert_PASS(check(ttFont))

    # If we add 'ital' it must FAIL:
    from fontTools.ttLib.tables._f_v_a_r import Axis
    new_axis = Axis()
    new_axis.axisTag = "ital"
    ttFont["fvar"].axes.append(new_axis)
    assert_results_contain(check(ttFont),
                           FAIL, 'unsupported-ital')

    # Then we reload the font and add 'opsz'
    # so it must also FAIL:
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    new_axis = Axis()
    new_axis.axisTag = "slnt"
    ttFont["fvar"].axes.append(new_axis)
    assert_results_contain(check(ttFont),
                           FAIL, 'unsupported-slnt')


def test_check_varfont_grade_reflow():
    """ Ensure VFs with the GRAD axis do not vary horizontal advance. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/varfont/grade_reflow")

    ttFont = TTFont(TEST_FILE("BadGrades/BadGrades-VF.ttf"))
    assert_results_contain(check(ttFont),
                           FAIL, 'grad-causes-reflow')

    # Zero out the horizontal advances
    gvar = ttFont["gvar"]
    for glyph, deltas in gvar.variations.items():
        for delta in deltas:
            if "GRAD" not in delta.axes:
                continue
            if delta.coordinates:
                delta.coordinates = delta.coordinates[:-4] + [(0,0)] * 4

    # But the kern rules should still be a problem
    assert_results_contain(check(ttFont),
                           FAIL, 'grad-kern-causes-reflow')

    ttFont["GPOS"].table.LookupList.Lookup = []
    assert_PASS(check(ttFont))


def test_check_gfaxisregistry_bounds():
    """Validate METADATA.pb axes values are within gf-axisregistry bounds."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/gf-axisregistry_bounds")

    # Our reference varfont, CabinVF, has good axes bounds:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    # The first axis declared in this family is 'wdth' (Width)
    # And the GF Axis Registry expects this axis to have a range
    # not broader than min: 25 / max: 200
    # So...
    md = check["family_metadata"]
    md.axes[0].min_value = 20
    assert_results_contain(check(ttFont, {"family_metadata": md}),
                           FAIL, "bad-axis-range")

    md.axes[0].min_value = 25
    md.axes[0].max_value = 250
    assert_results_contain(check(ttFont, {"family_metadata": md}),
                           FAIL, "bad-axis-range")


def test_check_gf_axisregistry_valid_tags():
    """Validate METADATA.pb axes tags are defined in gf-axisregistry."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/gf-axisregistry_valid_tags")

    # The axis tags in our reference varfont, CabinVF,
    # are properly defined in the registry:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    md = check["family_metadata"]
    md.axes[0].tag = "crap" # I'm pretty sure this one wont ever be included in the registry
    assert_results_contain(check(ttFont, {"family_metadata": md}),
                           FAIL, "bad-axis-tag")


def test_check_gf_axisregistry_fvar_axis_defaults():
    """Validate METADATA.pb axes tags are defined in gf-axisregistry."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/gf-axisregistry/fvar_axis_defaults")

    # The default value for the axes in this reference varfont
    # are properly registered in the registry:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    # And this value surely doen't map to a fallback name in the registry
    ttFont['fvar'].axes[0].defaultValue = 123
    assert_results_contain(check(ttFont),
                           FAIL, "not-registered")


def test_check_STAT_gf_axisregistry():
    """Validate STAT particle names and values match the fallback names in GFAxisRegistry."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/STAT/gf-axisregistry")

    # Our reference varfont, CabinVF,
    # has "Regular", instead of "Roman" in its 'ital' axis on the STAT table:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_results_contain(check(ttFont),
                           FAIL, "invalid-name")

    # LibreCaslonText is good though:
    ttFont = TTFont(TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf"))
    assert_PASS(check(ttFont))

    # Let's break it by setting an invalid coordinate for "Bold":
    assert ttFont['STAT'].table.AxisValueArray.AxisValue[3].ValueNameID == ttFont['name'].names[4].nameID
    assert ttFont['name'].names[4].toUnicode() == "Bold"
    ttFont['STAT'].table.AxisValueArray.AxisValue[3].Value = 800 # instead of the expected 700
    # Note: I know it is AxisValue[3] and names[4] because I inspected the font using ttx.
    assert_results_contain(check(ttFont),
                           FAIL, "bad-coordinate")

    # Let's remove all Axis Values. This will fail since we Google Fonts
    # requires them.
    ttFont['STAT'].table.AxisValueArray = None
    assert_results_contain(check(ttFont),
                           FAIL, "missing-axis-values")


def test_check_metadata_consistent_axis_enumeration():
    """Validate VF axes match the ones declared on METADATA.pb."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/consistent_axis_enumeration")

    # The axis tags of CabinVF,
    # are properly declared on its METADATA.pb:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    md = check["family_metadata"]
    md.axes[1].tag = "wdth" # this effectively removes the "wght" axis while not adding an extra one
    assert_results_contain(check(ttFont, {"family_metadata": md}),
                           FAIL, "missing-axes")

    md.axes[1].tag = "ouch" # and this is an unwanted extra axis
    assert_results_contain(check(ttFont, {"family_metadata": md}),
                           FAIL, "extra-axes")


def test_check_STAT_axis_order():
    """Check axis ordering on the STAT table."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/STAT/axis_order")

    fonts = [TEST_FILE("cabinvf/Cabin[wdth,wght].ttf")]
    assert_results_contain(check(fonts),
                           INFO, "summary")

    fonts = [TEST_FILE("merriweather/Merriweather-Regular.ttf")]
    assert_results_contain(check(fonts),
                           SKIP, "missing-STAT")

    # A real-world case here would be a corrupted TTF file.
    # This clearly is not a TTF, but is good enough for testing:
    fonts = [TEST_FILE("merriweather/METADATA.pb")]
    assert_results_contain(check(fonts),
                           ERROR, "bad-font")


def test_check_metadata_escaped_strings():
    """Ensure METADATA.pb does not use escaped strings."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/escaped_strings")

    good = TEST_FILE("issue_2932/good/SomeFont-Regular.ttf")
    assert_PASS(check(good))

    bad = TEST_FILE("issue_2932/bad/SomeFont-Regular.ttf")
    assert_results_contain(check(bad),
                           FAIL, "escaped-strings")


def test_check_metadata_designer_profiles():
    """METADATA.pb: Designer is listed with the correct name on
       the Google Fonts catalog of designers?"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/designer_profiles")

    # Delve Withrington is still not listed on the designers catalog.
    # Note: Once it is listed, this code-test will start failing and will need to be updated.
    font = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_results_contain(check(font),
                           WARN, "profile-not-found")

    # Cousine lists designers: "Multiple Designers"
    font = TEST_FILE("cousine/Cousine-Regular.ttf")
    assert_results_contain(check(font),
                           FAIL, "multiple-designers")

    # This reference Merriweather font family lists "Sorkin Type" in its METADATA.pb file.
    # And this foundry has a good profile on the catalog.
    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    assert_PASS(check(font))

    # TODO: FAIL, "mismatch"
    # TODO: FAIL, "link-field"
    # TODO: FAIL, "missing-avatar"
    # TODO: FAIL, "bad-avatar-filename"


def test_check_mandatory_avar_table():
    """Ensure variable fonts include an avar table."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/mandatory_avar_table")

    ttFont = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_PASS(check(ttFont))

    del ttFont["avar"]
    assert_results_contain(check(ttFont),
                           FAIL, "missing-avar")


def test_check_description_family_update():
    """On a family update, the DESCRIPTION.en_us.html file should ideally also be updated."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/family_update")

    font = TEST_FILE("abeezee/ABeeZee-Regular.ttf")
    ABEEZEE_DESC = ('https://raw.githubusercontent.com/google/fonts/'
                    'main/ofl/abeezee/DESCRIPTION.en_us.html')
    import requests
    desc = requests.get(ABEEZEE_DESC).text
    assert_results_contain(check(font, {'description': desc}),
                           FAIL, "description-not-updated")

    assert_PASS(check(font, {'description': desc + '\nSomething else...'}))


def test_check_os2_use_typo_metrics():
    """All non-CJK fonts checked with the googlefonts profile
    should have OS/2.fsSelection bit 7 (USE TYPO METRICS) set."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/os2/use_typo_metrics")

    ttFont = TTFont(TEST_FILE("abeezee/ABeeZee-Regular.ttf"))
    fsel = ttFont["OS/2"].fsSelection

    # set bit 7
    ttFont["OS/2"].fsSelection = fsel | (1 << 7)
    assert_PASS(check(ttFont))

    # clear bit 7
    ttFont["OS/2"].fsSelection = fsel & ~(1 << 7)
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-os2-fsselection-bit7')


# TODO: If I recall correctly, there was something wrong with
#       code-tests that try to ensure a check skips.
#       I will have to review this one at some point to verify
#       if that's the reason for this test not working properly.
#
#              -- Felipe Sanches (May 31, 2021)
def TODO_test_check_os2_use_typo_metrics_with_cjk():
    """All CJK fonts checked with the googlefonts profile should skip this check"""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/os2/use_typo_metrics")

    tt_pass_clear = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))
    tt_pass_set = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))

    fs_selection = 0

    # test skip with font that contains cleared bit
    tt_pass_clear["OS/2"].fsSelection = fs_selection
    # test skip with font that contains set bit
    tt_pass_set["OS/2"].fsSelection = fs_selection | (1 << 7)

    assert_SKIP(check(tt_pass_clear))
    assert_SKIP(check(tt_pass_set))


def test_check_missing_small_caps_glyphs():
    """Check small caps glyphs are available."""
    #check = CheckTester(googlefonts_profile,
    #                    "com.google.fonts/check/missing_small_caps_glyphs")
    # TODO: Implement-me!


def test_check_stylisticset_description():
    """Ensure Stylistic Sets have description."""
    #check = CheckTester(googlefonts_profile,
    #                    "com.google.fonts/check/stylisticset_description")
    # TODO: Implement-me!


def test_check_meta_script_lang_tags():
    """Ensure font has ScriptLangTags in the 'meta' table."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/meta/script_lang_tags")

    # This sample font from the Noto project declares
    # the script/lang tags in the meta table correctly:
    ttFont = TTFont(TEST_FILE("meta_tag/NotoSansPhagsPa-Regular-with-meta.ttf"))
    assert_results_contain(check(ttFont), INFO, 'dlng-tag')
    assert_results_contain(check(ttFont), INFO, 'slng-tag')

    del ttFont["meta"].data['dlng']
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-dlng-tag')

    del ttFont["meta"].data['slng']
    assert_results_contain(check(ttFont),
                           FAIL, 'missing-slng-tag')

    del ttFont["meta"]
    assert_results_contain(check(ttFont),
                           WARN, 'lacks-meta-table')


def test_check_no_debugging_tables():
    """Ensure fonts do not contain any preproduction tables."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/no_debugging_tables")

    ttFont = TTFont(TEST_FILE("overpassmono/OverpassMono-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           WARN, 'has-debugging-tables')

    del ttFont["FFTM"]
    assert_PASS(check(ttFont))


def test_check_metadata_family_directory_name():
    """Check family directory name."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/family_directory_name")

    ttFont = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_PASS(check(ttFont))

    # Note:
    # Here I explicitly pass 'family_metadata' to avoid it being recomputed
    # after I make the family_directory wrong:
    assert_results_contain(check(ttFont, {'family_metadata': check['family_metadata'],
                                          'family_directory': 'overpass'}),
                           FAIL, 'bad-directory-name')


def test_check_render_own_name():
    """Check family directory name."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/render_own_name")

    ttFont = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_PASS(check(ttFont))

    ttFont = TEST_FILE("noto_sans_tamil_supplement/NotoSansTamilSupplement-Regular.ttf")
    assert_results_contain(check(ttFont),
                           FAIL, 'render-own-name')


def test_check_repo_sample_image():
    """Check README.md has a sample image."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/repo/sample_image")

    # That's what we'd like to see:
    # README.md including a sample image and highlighting it in the
    # upper portion of the document (no more than 10 lines from the top).
    readme = TEST_FILE("issue_2898/good/README.md")
    assert_PASS(check(readme))

    # This one is still good, but places the sample image too late in the page:
    readme = TEST_FILE("issue_2898/not-ideal-placement/README.md")
    assert_results_contain(check(readme),
                           WARN, 'not-ideal-placement')

    # Here's a README.md in a project completely lacking such sample image.
    # This will likely become a FAIL in the future:
    readme = TEST_FILE("issue_2898/no-sample/README.md")
    assert_results_contain(check(readme),
                           WARN, 'no-sample') # FIXME: Make this a FAIL!

    # This is really broken, as it references an image that is not available:
    readme = TEST_FILE("issue_2898/image-missing/README.md")
    assert_results_contain(check(readme),
                           FAIL, 'image-missing')

    # An here a README.md that does not include any sample image,
    # while an image file can be found within the project's directory tree.
    # This image could potentially be a font sample, so we let the user know
    # that it might be the case:
    readme = TEST_FILE("issue_2898/image-not-displayed/README.md")
    assert_results_contain(check(readme),
                           WARN, 'image-not-displayed')


def test_check_metadata_can_render_samples():
    """Check README.md has a sample image."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/can_render_samples")

    # Cabin's METADATA.pb does not have sample_glyphs entry
    metadata_file = TEST_FILE("cabin/METADATA.pb")
    assert_results_contain(check(metadata_file),
                           INFO, 'no-samples')

    # We add a small set of latin glyphs
    # that we're sure Cabin supports:
    md = check["family_metadata"]
    md.sample_glyphs["Letters"] = "abcdefghijklmnopqrstuvyz0123456789"
    assert_PASS(check(metadata_file, {"family_metadata": md}))

    # And now with Tamil glyphs that Cabin lacks:
    md.sample_glyphs["Numbers"] = "𑿀 𑿁 𑿂 𑿃 𑿄 𑿅 𑿆 𑿇 𑿈 𑿉 𑿊 𑿋 𑿌 𑿍 𑿎 𑿏 𑿐 𑿑 𑿒 𑿓 𑿔"
    assert_results_contain(check(metadata_file, {"family_metadata": md}),
                           FAIL, 'sample-glyphs')

    # TODO: expand the check to also validate sample_text fields


def test_check_description_urls():
    """URLs on DESCRIPTION file must not display http(s) prefix."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/description/urls")

    font = TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf")
    assert_PASS(check(font))

    font = TEST_FILE("cabinvfbeta/CabinVFBeta.ttf")
    assert_results_contain(check(font),
                           WARN, 'prefix-found')

    good_desc = check["description"].replace(">https://", ">")
    assert_PASS(check(font, {"description": good_desc}))


def test_check_metadata_unsupported_subsets():
    """Check for METADATA subsets with zero support."""
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/unsupported_subsets")

    font = TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf")
    assert_PASS(check(font))

    md = check["family_metadata"]
    md.subsets.extend(["foo"])
    assert_results_contain(check(font, {"family_metadata": md}),
                           WARN, 'unknown-subset')

    del md.subsets[:]
    md.subsets.extend(["cyrillic"])
    assert_results_contain(check(font, {"family_metadata": md}),
                           WARN, 'unsupported-subset')


def test_check_metadata_category_hints():
    """ Check if category on METADATA.pb matches what can be inferred from the family name. """
    check = CheckTester(googlefonts_profile,
                        "com.google.fonts/check/metadata/category_hints")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font),
                "with a familyname without any of the keyword hints...")

    md = check["family_metadata"]
    md.name = "Seaweed Script"
    md.category = "DISPLAY"
    assert_results_contain(check(font, {"family_metadata": md}),
                           WARN, 'inferred-category',
                           f'with a bad category "{md.category}" for familyname "{md.name}"...')

    md.name = "Red Hat Display"
    md.category = "SANS_SERIF"
    assert_results_contain(check(font, {"family_metadata": md}),
                           WARN, 'inferred-category',
                           f'with a bad category "{md.category}" for familyname "{md.name}"...')

    md.name = "Seaweed Script"
    md.category = "HANDWRITING"
    assert_PASS(check(font, {"family_metadata": md}),
                f'with a good category "{md.category}" for familyname "{md.name}"...')

    md.name = "Red Hat Display"
    md.category = "DISPLAY"
    assert_PASS(check(font, {"family_metadata": md}),
                f'with a good category "{md.category}" for familyname "{md.name}"...')
