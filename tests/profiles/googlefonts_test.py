import pytest
import os
from fontTools.ttLib import TTFont

from fontbakery.constants import (NameID,
                                  PlatformID,
                                  WindowsEncodingID,
                                  WindowsLanguageID,
                                  MacintoshEncodingID,
                                  MacintoshLanguageID)
from fontbakery.utils import (assert_results_contain,
                              assert_PASS,
                              portable_path,
                              TEST_FILE)

from fontbakery.profiles import googlefonts
from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            )

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
    TEST_FILE("cabin/CabinCondensed-Regular.ttf"),
    TEST_FILE("cabin/CabinCondensed-Medium.ttf"),
    TEST_FILE("cabin/CabinCondensed-Bold.ttf"),
    TEST_FILE("cabin/CabinCondensed-SemiBold.ttf")
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
    runner = CheckRunner(profile, values, explicit_checks=['com.google.fonts/check/vendor_id'])

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_canonical_filename as check

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

    # TODO: FAIL, 'bad-static-filename'
    # TODO: FAIL, 'varfont-with-static-filename'


def test_check_description_broken_links():
    """ Does DESCRIPTION file contain broken links ? """
    from fontbakery.profiles.googlefonts import (
        com_google_fonts_check_description_broken_links as check,
        description,
        description_html,
        descfile)

    good_desc = description(descfile(TEST_FILE("cabin/Cabin-Regular.ttf")))
    assert_PASS(check(description_html(good_desc)),
                'with description file that has no links...')

    good_desc += ("<a href='http://example.com'>Good Link</a>"
                  "<a href='http://fonts.google.com'>Another Good One</a>")
    assert_PASS(check(description_html(good_desc)),
                'with description file that has good links...')

    good_desc += "<a href='mailto:juca@members.fsf.org'>An example mailto link</a>"
    assert_results_contain(check(description_html(good_desc)),
                           INFO, "email",
                           'with a description file containing "mailto" links...')

    assert_PASS(check(description_html(good_desc)),
                'with a description file containing "mailto" links...')

    bad_desc = good_desc + "<a href='http://thisisanexampleofabrokenurl.com/'>This is a Bad Link</a>"
    assert_results_contain(check(description_html(bad_desc)),
                           FAIL, 'broken-links',
                           'with a description file containing a known-bad URL...')

    #TODO: WARN, 'timeout'


def test_check_description_git_url():
    """ Does DESCRIPTION file contain an upstream Git repo URL? """
    from fontbakery.profiles.googlefonts import (
        com_google_fonts_check_description_git_url as check,
        description,
        description_html,
        descfile)

    # TODO: test INFO 'url-found'

    bad_desc = description(descfile(TEST_FILE("cabin/Cabin-Regular.ttf")))
    assert_results_contain(check(description_html(bad_desc)),
                           FAIL, 'lacks-git-url',
                           'with description file that has no git repo URLs...')

    good_desc = ("<a href='https://github.com/uswds/public-sans'>Good URL</a>"
                 "<a href='https://gitlab.com/smc/fonts/uroob'>Another Good One</a>")
    assert_PASS(check(description_html(good_desc)),
                'with description file that has good links...')

    bad_desc = "<a href='https://v2.designsystem.digital.gov'>Bad URL</a>"
    assert_results_contain(check(description_html(bad_desc)),
                           FAIL, 'lacks-git-url',
                           'with description file that has false git in URL...')


def test_check_description_valid_html():
    """ DESCRIPTION file is a propper HTML snippet ? """
    from fontbakery.profiles.googlefonts import (
        com_google_fonts_check_description_valid_html as check,
        descfile,
        description)

    good_descfile = descfile(TEST_FILE("nunito/Nunito-Regular.ttf"))
    good_desc = description(good_descfile)
    assert_PASS(check(good_descfile, good_desc),
                'with description file that contains a good HTML snippet...')

    bad_descfile = TEST_FILE("cabin/FONTLOG.txt") # :-)
    bad_desc = description(bad_descfile)
    assert_results_contain(check(bad_descfile, bad_desc),
                           FAIL, 'lacks-paragraph',
                           'with a known-bad file (without HTML paragraph tags)...')

    bad_desc = f"<html>{description}</html>"
    assert_results_contain(check(bad_descfile, bad_desc),
                           FAIL, 'html-tag',
                           'with description file that contains the <html> tag...')

    bad_desc = ("<p>This example has the & caracter,"
                " but does not escape it with an HTML entity code."
                " It should use &amp; instead."
                "</p>")
    assert_results_contain(check(bad_descfile, bad_desc),
                           FAIL, 'malformed-snippet',
                           'with a known-bad file (not using HTML entity syntax)...')


def test_check_description_min_length():
    """ DESCRIPTION.en_us.html must have more than 200 bytes. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_description_min_length as check

    bad_length = 'a' * 199
    assert_results_contain(check(bad_length),
                           FAIL, 'too-short',
                           'with 199-byte buffer...')

    bad_length = 'a' * 200
    assert_results_contain(check(bad_length),
                           FAIL, 'too-short',
                           'with 200-byte buffer...')

    good_length = 'a' * 201
    assert_PASS(check(good_length),
                'with 201-byte buffer...')


def test_check_description_max_length():
    """ DESCRIPTION.en_us.html must have less than 1000 bytes. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_description_max_length as check

    bad_length = 'a' * 1001
    assert_results_contain(check(bad_length),
                           FAIL, "too-long",
                           'with 1001-byte buffer...')

    bad_length = 'a' * 1000
    assert_results_contain(check(bad_length),
                           FAIL, "too-long",
                           'with 1000-byte buffer...')

    good_length = 'a' * 999
    assert_PASS(check(good_length),
                'with 999-byte buffer...')


def test_check_description_eof_linebreak():
    """ DESCRIPTION.en_us.html should end in a linebreak. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_description_eof_linebreak as check

    bad = ("We want to avoid description files\n"
           "without an end-of-file linebreak\n"
           "like this one.")
    assert_results_contain(check(bad),
                           WARN, "missing-eof-linebreak",
                           'when we lack an end-of-file linebreak...')

    good = ("On the other hand, this one\n"
            "is good enough.\n")
    assert_PASS(check(good),
                'when we add one...')


def test_check_name_family_and_style_max_length(): 
    """ Combined length of family and style must not exceed 27 characters. """
    from fontbakery.profiles.googlefonts import ( 
        com_google_fonts_check_name_family_and_style_max_length as check) 

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


def test_check_name_line_breaks():
    """ Name table entries should not contain line-breaks. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_line_breaks as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_rfn as check

    test_font = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font["name"].setName("Bla Reserved Font Name", 5, 3, 1, 0x409)
    assert_results_contain(check(test_font),
                           FAIL, 'rfn',
                           'with "Reserved Font Name" on a name table entry...')


def test_check_metadata_parses():
    """ Check METADATA.pb parse correctly. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_metadata_parses as check

    good = portable_path("data/test/merriweather")
    assert_PASS(check(good),
                'with a good METADATA.pb file...')

    skip = portable_path("data/test/slabo")
    assert_results_contain(check(skip),
                           SKIP, 'file-not-found',
                           'with a missing METADATA.pb file...')

    bad = portable_path("data/test/broken_metadata")
    assert_results_contain(check(bad),
                           FAIL, 'parsing-error',
                           'with a bad METADATA.pb file...')


def test_check_metadata_unknown_designer():
    """ Font designer field in METADATA.pb must not be 'unknown'. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_unknown_designer as check,
                                                 family_metadata)
    good = family_metadata(portable_path("data/test/merriweather"))
    assert_PASS(check(good),
                'with a good METADATA.pb file...')

    bad = family_metadata(portable_path("data/test/merriweather"))
    bad.designer = "unknown"
    assert_results_contain(check(bad),
                           FAIL, 'unknown-designer',
                           'with a bad METADATA.pb file...')


def test_check_metadata_designer_values():
    """ Multiple values in font designer field in
        METADATA.pb must be separated by commas. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_designer_values as check,
                                                 family_metadata)
    good = family_metadata(portable_path("data/test/merriweather"))
    assert_PASS(check(good),
                'with a good METADATA.pb file...')

    good.designer = "Pentagram, MCKL"
    assert_PASS(check(good),
                'with a good multiple-designers string...')

    bad = family_metadata(portable_path("data/test/merriweather"))
    bad.designer = "Pentagram / MCKL" # This actually happened on an
                                      # early version of the Red Hat Text family
    assert_results_contain(check(bad),
                           FAIL, 'slash',
                           'with a bad multiple-designers string'
                           ' (names separated by a slash char)...')


def test_check_metadata_broken_links():
    """ Does DESCRIPTION file contain broken links? """
    from fontbakery.profiles.googlefonts import (
        com_google_fonts_check_metadata_broken_links as check)
    # TODO: Implement-me!
    # INFO, "email"
    # WARN, "timeout"
    # FAIL, "broken-links"


def test_check_metadata_undeclared_fonts():
    """ Ensure METADATA.pb lists all font binaries. """
    from fontbakery.profiles.googlefonts_conditions import family_metadata
    from fontbakery.profiles.googlefonts import (
        com_google_fonts_check_metadata_undeclared_fonts as check)

    # Our reference Nunito family is know to be good here.
    family_dir = portable_path("data/test/nunito")
    assert_PASS(check(family_metadata(family_dir), family_dir))

    # Our reference Cabin family has files that are not declared in its METADATA.pb:
    # - CabinCondensed-Medium.ttf
    # - CabinCondensed-SemiBold.ttf
    # - CabinCondensed-Regular.ttf
    # - CabinCondensed-Bold.ttf
    family_dir = portable_path("data/test/cabin")
    assert_results_contain(check(family_metadata(family_dir), family_dir),
                           FAIL, 'file-not-declared')

    # We placed an additional file on a subdirectory of our reference
    # OverpassMono family with the name "another_directory/ThisShouldNotBeHere.otf"
    family_dir = portable_path("data/test/overpassmono")
    assert_results_contain(check(family_metadata(family_dir), family_dir),
                           WARN, 'font-on-subdir')

    # We do accept statics folder though!
    # Jura is an example:
    family_dir = portable_path("data/test/varfont/jura")
    assert_PASS(check(family_metadata(family_dir), family_dir))


# TODO: re-enable after addressing issue #1998
def DISABLED_test_check_family_equal_numbers_of_glyphs(mada_ttFonts, cabin_ttFonts):
    """ Fonts have equal numbers of glyphs? """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_family_equal_numbers_of_glyphs as check

    # our reference Cabin family is know to be good here.
    assert_PASS(check(cabin_ttFonts),
                'with a good family.')

    # our reference Mada family is bad here with 407 glyphs on most font files
    # except the Black and the Medium, that both have 408 glyphs.
    assert_results_contain(check(mada_ttFonts),
                           FAIL, 'glyph-count-diverges',
                           'with fonts that diverge on number of glyphs.')


# TODO: re-enable after addressing issue #1998
def DISABLED_test_check_family_equal_glyph_names(mada_ttFonts, cabin_ttFonts):
    """ Fonts have equal glyph names? """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_family_equal_glyph_names as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_fstype as check

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


def get_check(profile, checkid):
    def _checker(value):
        from fontbakery.fonts_profile import execute_check_once
        if isinstance(value, str):
            return execute_check_once(profile, checkid, value)

        elif isinstance(value, TTFont):
            return execute_check_once(profile, checkid, value.reader.file.name,
                                      {'ttFont': value})
    return _checker


def test_check_vendor_id():
    """ Checking OS/2 achVendID """
    check = get_check(googlefonts, "com.google.fonts/check/vendor_id")

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


def NOT_IMPLEMENTED__test_check_glyph_coverage():
    """ Check glyph coverage. """
    #from fontbakery.profiles.googlefonts import com_google_fonts_check_glyph_coverage as check
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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_unwanted_chars as check

    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           FAIL, 'unwanted-chars',
                           'with a bad font...')

    # Our reference Cabin Regular is know to be good here.
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont),
                'with a good font...')


def test_check_usweightclass():
    """ Checking OS/2 usWeightClass. """
    check = get_check(googlefonts, "com.google.fonts/check/usweightclass")

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
                           FAIL, None, #FIXME! We need a message keyword here
                           f'with bad font "{font}"...')

    ttFont['OS/2'].usWeightClass = 250
    assert_PASS(check(ttFont),
                f'with good font "{font}" (usWeightClass = 250) ...')

    font = TEST_FILE("rokkitt/Rokkitt-ExtraLight.otf")
    ttFont = TTFont(font)
    assert_results_contain(check(ttFont),
                           FAIL, None, #FIXME! We need a message keyword here
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
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_family_has_license as check,
                                                 licenses)

    # The lines maked with 'hack' below are meant to
    # not let fontbakery's own license to mess up
    # this code test.
    detected_licenses = licenses(portable_path("data/test/028/multiple"))
    detected_licenses.pop(-1) # hack
    assert_results_contain(check(detected_licenses),
                           FAIL, 'multiple',
                           'with multiple licenses...')

    detected_licenses = licenses(portable_path("data/test/028/none"))
    detected_licenses.pop(-1) # hack
    assert_results_contain(check(detected_licenses),
                           FAIL, 'no-license',
                           'with no license...')

    detected_licenses = licenses(portable_path("data/test/028/pass_ofl"))
    detected_licenses.pop(-1) # hack
    assert_PASS(check(detected_licenses),
                'with a single OFL license...')

    detected_licenses = licenses(portable_path("data/test/028/pass_apache"))
    detected_licenses.pop(-1) # hack
    assert_PASS(check(detected_licenses),
                'with a single Apache license...')


def test_check_name_license(mada_ttFonts):
    """ Check copyright namerecords match license file. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_license as check

    # Our reference Mada family has its copyright name records properly set
    # identifying it as being licensed under the Open Font License
    license = 'OFL.txt'
    wrong_license = 'LICENSE.txt' # Apache

    for ttFont in mada_ttFonts:
        assert_PASS(check(ttFont, license),
                    'with good fonts ...')

    for ttFont in mada_ttFonts:
        assert_results_contain(check(ttFont, wrong_license),
                               FAIL, 'wrong',
                               'with wrong entry values ...')

    for ttFont in mada_ttFonts:
        delete_name_table_id(ttFont, NameID.LICENSE_DESCRIPTION)
        assert_results_contain(check(ttFont, wrong_license),
                               FAIL, 'missing',
                               'with missing copyright namerecords ...')

    # TODO:
    # WARN, "http" / "http-in-description"


def NOT_IMPLEMENTED_test_check_name_license_url():
    """ License URL matches License text on name table? """
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_name_license_url as check
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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_description_max_length as check

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
    check = get_check(googlefonts, "com.google.fonts/check/hinting_impact")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(check(font),
                           INFO, 'size-impact',
                           'this check always emits an INFO result...')
    # TODO: test the CFF code-path


def test_check_name_version_format():
    """ Version format is correct in 'name' table ? """
    check = get_check(googlefonts, "com.google.fonts/check/name/version_format")

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
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_old_ttfautohint as check
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, code="lacks-version-strings"
    # - INFO, code="version-not-detected"  "Could not detect which version of ttfautohint
    #                                       was used in this font."
    # - WARN, code="old-ttfa"  "detected an old ttfa version"
    # - PASS
    # - FAIL, code="parse-error"


@pytest.mark.parametrize("expected_status,expected_keyword,reason,fontfile",[
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
def test_check_has_ttfautohint_params(expected_status, expected_keyword, reason, fontfile):
    """ Font has ttfautohint params? """
    check = get_check(googlefonts, "com.google.fonts/check/has_ttfautohint_params")
    assert_results_contain(check(TTFont(fontfile)),
                           expected_status, expected_keyword,
                           reason)


def test_check_epar():
    """ EPAR table present in font? """
    check = get_check(googlefonts, "com.google.fonts/check/epar")

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
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_gasp as check
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
    check = get_check(googlefonts, "com.google.fonts/check/name/familyname_first_char")

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_ascii_only_entries as check

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
    check = get_check(googlefonts, "com.google.fonts/check/metadata/listed_on_gfonts")
    
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


# FIXME: This check is currently disabled:
# - Review and re-enable.
# - Implement the test.
def NOT_IMPLEMENTED_test_check_metadata_profiles_csv():
    """ METADATA.pb: Designer exists in Google Fonts profiles.csv? """
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_metadata_profiles_csv as check
    # TODO: Implement-me!
    #
    # code-paths:
    # FAIL, "empty"
    # SKIP, "multiple"
    # WARN, "not-listed"
    # WARN, "csv-not-fetched"


def test_check_metadata_unique_full_name_values():
    """ METADATA.pb: check if fonts field only has unique "full_name" values. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_unique_full_name_values as check,
                family_metadata)

    # Our reference FamilySans family is good:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)
    assert_PASS(check(md),
                'with a good family...')

    # then duplicate a full_name entry to make it FAIL:
    md.fonts[0].full_name = md.fonts[1].full_name
    assert_results_contain(check(md),
                           FAIL, 'duplicated',
                           'with a duplicated full_name entry.')


def test_check_metadata_unique_weight_style_pairs():
    """ METADATA.pb: check if fonts field only contains unique style:weight pairs. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_unique_weight_style_pairs as check,
                family_metadata)
    # Our reference FamilySans family is good:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)
    assert_PASS(check(md),
                'with a good family...')

    # then duplicate a pair of style & weight entries to make it FAIL:
    md.fonts[0].style = md.fonts[1].style
    md.fonts[0].weight = md.fonts[1].weight
    assert_results_contain(check(md),
                           FAIL, 'duplicated',
                           'with a duplicated pair of style & weight entries')


def test_check_metadata_license():
    """ METADATA.pb license is "APACHE2", "UFL" or "OFL"? """
    from fontbakery.profiles.shared_conditions import family_directory
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_license as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    md = family_metadata(family_directory(font))

    good_licenses = ["APACHE2", "UFL", "OFL"]
    some_bad_values = ["APACHE", "Apache", "Ufl", "Ofl", "Open Font License"]

    for good in good_licenses:
        md.license = good
        assert_PASS(check(md),
                    f': {good}')

    for bad in some_bad_values:
        md.license = bad
        assert_results_contain(check(md),
                               FAIL, 'bad-license',
                               f': {bad}')


def test_check_metadata_menu_and_latin():
    """ METADATA.pb should contain at least "menu" and "latin" subsets. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_menu_and_latin as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)

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

    for good in good_cases:
        del md.subsets[:]
        md.subsets.extend(good)
        assert_PASS(check(md),
                    f'with subsets = {good}')

    for bad in bad_cases:
        del md.subsets[:]
        md.subsets.extend(bad)
        assert_results_contain(check(md),
                               FAIL, 'missing',
                               f'with subsets = {bad}')


def test_check_metadata_subsets_order():
    """ METADATA.pb subsets should be alphabetically ordered. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_subsets_order as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)

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

    for good in good_cases:
        del md.subsets[:]
        md.subsets.extend(good)
        assert_PASS(check(md),
                    f'with subsets = {good}')

    for bad in bad_cases:
        del md.subsets[:]
        md.subsets.extend(bad)
        assert_results_contain(check(md),
                               FAIL, 'not-sorted',
                               f'with subsets = {bad}')


def test_check_metadata_includes_production_subsets():
    """Check METADATA.pb has production subsets."""
    from fontbakery.profiles.googlefonts \
        import com_google_fonts_check_metadata_includes_production_subsets as check
    from fontbakery.profiles.googlefonts_conditions import (production_metadata,
                                                            family_metadata)
    from fontbakery.profiles.shared_conditions import family_directory

    # We need to use a family that is already in production
    # Our reference Cabin is known to be good
    family_meta = family_metadata(family_directory(cabin_fonts[0]))

    # So it must PASS the check:
    assert_PASS(check(family_meta, production_metadata()),
                "with a good METADATA.pb for this family...")

    # Then we FAIL the check by removing a subset:
    family_meta.subsets.pop()
    assert_results_contain(check(family_meta, production_metadata()),
                           FAIL, 'missing-subsets',
                           'with a bad METADATA.pb (last subset has been removed)...')


def test_check_metadata_copyright():
    """ METADATA.pb: Copyright notice is the same in all fonts? """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_copyright as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)

    # We know its copyright notices are consistent:
    assert_PASS(check(md),
                'with consistent copyright notices on FamilySans...')

    # Now we make them diverge:
    md.fonts[1].copyright = md.fonts[0].copyright + " arbitrary suffix!" # to make it different

    # And now the check must FAIL:
    assert_results_contain(check(md),
                           FAIL, 'inconsistency',
                           'with diverging copyright notice strings...')


def test_check_metadata_familyname():
    """ Check that METADATA.pb family values are all the same. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_familyname as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)

    # We know its family name entries on METADATA.pb are consistent:
    assert_PASS(check(md),
                'with consistent family name...')

    # Now we make them diverge:
    md.fonts[1].name = md.fonts[0].name + " arbitrary suffix!" # to make it different

    # And now the check must FAIL:
    assert_results_contain(check(md),
                           FAIL, 'inconsistency',
                           'With diverging Family name metadata entries...')


def test_check_metadata_has_regular():
    """ METADATA.pb: According Google Fonts standards, families should have a Regular style. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_has_regular as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)

    # We know that Family Sans has got a regular declares in its METADATA.pb file:
    assert_PASS(check(md),
                'with Family Sans, a family with a regular style...')

    # We remove the regular:
    for i, font in enumerate(md.fonts):
        if font.filename == "FamilySans-Regular.ttf":
            del md.fonts[i]

    # and make sure the check now FAILs:
    assert_results_contain(check(md),
                           FAIL, 'lacks-regular',
                           'with a METADATA.pb file without a regular...')


def test_check_metadata_regular_is_400():
    """ METADATA.pb: Regular should be 400. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_regular_is_400 as check,
                                                 family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    family_directory = portable_path("data/test/familysans")
    md = family_metadata(family_directory)

    # We know that Family Sans' Regular has a weight value equal to 400, so the check should PASS:
    assert_PASS(check(md),
                'with Family Sans, a family with regular=400...')

    # The we change the value for its regular:
    for i, font in enumerate(md.fonts):
        if font.filename == "FamilySans-Regular.ttf":
            md.fonts[i].weight = 500

    # and make sure the check now FAILs:
    assert_results_contain(check(md),
                           FAIL, 'not-400',
                           'with METADATA.pb with regular=500...')


def test_check_metadata_nameid_family_name():
    """ Checks METADATA.pb font.name field matches
        family name declared on the name table. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_nameid_family_name as check,
                font_metadata,
                family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    family_directory = portable_path("data/test/familysans")
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, font)
    ttFont = TTFont(font)

    # We know that Family Sans Regular is good here:
    assert_PASS(check(ttFont, font_meta))

    # Then cause it to fail:
    font_meta.name = "Foo"
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, "mismatch")

    # TODO: the failure-mode below seems more generic than the scope
    #       of this individual check. This could become a check by itself!
    #
    # code-paths:
    # - FAIL code="missing", "Font lacks a FONT_FAMILY_NAME entry"


def test_check_metadata_nameid_post_script_name():
    """ Checks METADATA.pb font.post_script_name matches
        postscript name declared on the name table. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_nameid_post_script_name as check,
                font_metadata,
                family_metadata)

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    family_directory = portable_path("data/test/familysans")
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, font)
    ttFont = TTFont(font)

    # We know that Family Sans Regular is good here:
    assert_PASS(check(ttFont, font_meta))

    # Then cause it to fail:
    font_meta.post_script_name = "Foo"
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'mismatch')

    # TODO: the failure-mode below seems more generic than the scope
    #       of this individual check. This could become a check by itself!
    #
    # code-paths:
    # - FAIL code="missing", "Font lacks a POSTSCRIPT_NAME"


def test_check_metadata_nameid_full_name():
    """ METADATA.pb font.fullname value matches fullname declared on the name table ? """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_nameid_full_name as check,
                font_metadata,
                family_metadata)
    import os

    # Our reference Merriweather-Regular is know to be good here
    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    family_directory = os.path.dirname(font)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, font)
    ttFont = TTFont(font)

    assert_PASS(check(ttFont, font_meta),
                'with a good font...')

    # here we change the font.fullname on the METADATA.pb
    # to introduce a "mismatch" error condition:
    good = font_meta.full_name
    font_meta.full_name = good + "bad-suffix"
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'mismatch',
                           'with mismatching fullname values...')

    # and restore the good value prior to the next test case:
    font_meta.full_name = good

    # And here we remove all FULL_FONT_NAME entries
    # in order to get a "lacks-entry" error condition:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            del ttFont["name"].names[i]
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'lacks-entry',
                           'when a font lacks FULL_FONT_NAME entries in its name table...')


def test_check_metadata_nameid_font_name():
    """ METADATA.pb font.name value should be same as the family name declared on the name table. """
    check = get_check(googlefonts, "com.google.fonts/check/metadata/nameid/font_name")

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
    from fontbakery.profiles.googlefonts import (
        com_google_fonts_check_metadata_match_fullname_postscript as check,
      font_metadata,
      family_metadata)

    regular_font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    lightitalic_font = TEST_FILE("merriweather/Merriweather-LightItalic.ttf")
    family_meta = family_metadata(portable_path("data/test/merriweather"))

    regular_meta = font_metadata(family_meta, regular_font)
    lightitalic_meta = font_metadata(family_meta, lightitalic_font)

    assert_PASS(check(lightitalic_meta),
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
    assert_results_contain(check(regular_meta),
                           FAIL, 'mismatch',
                           'with bad entries (Merriweather-Regular)...')
    #                       post_script_name: "Merriweather-Regular"
    #                       full_name:        "Merriweather"

    # fix the regular metadata:
    regular_meta.full_name = "Merriweather Regular"

    assert_PASS(check(regular_meta),
                'with good entries (Merriweather-Regular after full_name fix)...')
    #            post_script_name: "Merriweather-Regular"
    #            full_name:        "Merriweather Regular"


    # introduce an error in the metadata:
    regular_meta.full_name = "MistakenFont Regular"

    assert_results_contain(check(regular_meta),
                           FAIL, 'mismatch',
                           'with a mismatch...')
    #                       post_script_name: "Merriweather-Regular"
    #                       full_name:        "MistakenFont Regular"


def NOT_IMPLEMENTED_test_check_match_filename_postscript():
    """ METADATA.pb family.filename and family.post_script_name
        fields have equivalent values? """
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_match_filename_postscript as check
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
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_valid_name_values as check,
                style,
                family_metadata,
                font_metadata,
                font_familynames,
                typographic_familynames)

    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI:
        ttFont = TTFont(fontfile)
        font_style = style(fontfile)
        family_directory = os.path.dirname(fontfile)
        family_meta = family_metadata(family_directory)
        font_meta = font_metadata(family_meta, fontfile)
        font_fnames = font_familynames(ttFont)
        font_tfnames = []

        # So it must PASS the check:
        assert_PASS(check(font_style, font_meta, font_fnames, font_tfnames),
                    f'with a good RIBBI font ({fontfile})...')

        # And fail if it finds a bad font_familyname:
        font_fnames = ["WrongFamilyName"]
        assert_results_contain(check(font_style, font_meta, font_fnames, font_tfnames),
                               FAIL, 'mismatch',
                               f'with a bad RIBBI font ({fontfile})...')

    #we do the same for NON-RIBBI styles:
    for fontfile in MONTSERRAT_NON_RIBBI:
        ttFont = TTFont(fontfile)
        font_style = style(fontfile)
        family_directory = os.path.dirname(fontfile)
        family_meta = family_metadata(family_directory)
        font_meta = font_metadata(family_meta, fontfile)
        font_fnames = []
        font_tfnames = typographic_familynames(ttFont)

        # So it must PASS the check:
        assert_PASS(check(font_style,
                          font_meta,
                          font_fnames,
                          font_tfnames),
                    'with a good NON-RIBBI font ({fontfile})...')

        # And fail if it finds a bad font_familyname:
        font_tfnames = ["WrongFamilyName"]
        assert_results_contain(check(font_style, font_meta, font_fnames, font_tfnames),
                               FAIL, 'mismatch',
                               f'with a bad NON_RIBBI font ({fontfile})...')


def test_check_metadata_valid_full_name_values():
    """ METADATA.pb font.full_name field contains font name in right format ? """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_valid_full_name_values as check,
                style,
                family_metadata,
                font_metadata,
                font_familynames,
                typographic_familynames)

    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI:
        ttFont = TTFont(fontfile)
        font_style = style(fontfile)
        family_directory = os.path.dirname(fontfile)
        family_meta = family_metadata(family_directory)
        font_meta = font_metadata(family_meta, fontfile)
        font_fnames = font_familynames(ttFont)
        font_tfnames = []

        # So it must PASS the check:
        assert_PASS(check(font_style, font_meta, font_fnames, font_tfnames),
                    'with a good RIBBI font ({fontfile})...')

        # And fail if it finds a bad font_familyname:
        font_fnames = ["WrongFamilyName"]
        assert_results_contain(check(font_style, font_meta, font_fnames, font_tfnames),
                               FAIL, 'mismatch',
                               f'with a bad RIBBI font ({fontfile})...')

    #we do the same for NON-RIBBI styles:
    for fontfile in MONTSERRAT_NON_RIBBI:
        ttFont = TTFont(fontfile)
        font_style = style(fontfile)
        family_directory = os.path.dirname(fontfile)
        family_meta = family_metadata(family_directory)
        font_meta = font_metadata(family_meta, fontfile)
        font_fnames = []
        font_tfnames = typographic_familynames(ttFont)

        # So it must PASS the check:
        assert_PASS(check(font_style, font_meta, font_fnames, font_tfnames),
                    f'with a good NON-RIBBI font ({fontfile})...')

        # And fail if it finds a bad font_familyname:
        font_tfnames = ["WrongFamilyName"]
        assert_results_contain(check(font_style, font_meta, font_fnames, font_tfnames),
                               FAIL, 'mismatch',
                               f'with a bad NON_RIBBI font ({fontfile})...')


def test_check_metadata_valid_filename_values():
    """ METADATA.pb font.filename field contains font name in right format ? """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_valid_filename_values as check,
                family_metadata)

    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        family_directory = os.path.dirname(fontfile)
        meta = family_metadata(family_directory)

        # So it must PASS the check:
        assert_PASS(check(fontfile, meta),
                    f"with a good font ({fontfile})...")

        # And fail if it finds a bad filename:
        for font in meta.fonts:
            font.filename = "WrongFileName"
        assert_results_contain(check(fontfile, meta),
                               FAIL, 'bad-field',
                               f'with a bad font ({fontfile})...')


def test_check_metadata_valid_post_script_name_values():
    """ METADATA.pb font.post_script_name field contains font name in right format? """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_valid_post_script_name_values as check,
                family_metadata,
                font_metadata,
                font_familynames)

    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        family_directory = os.path.dirname(fontfile)
        family_meta = family_metadata(family_directory)
        font_meta = font_metadata(family_meta, fontfile)
        ttFont = TTFont(fontfile)
        font_fnames = font_familynames(ttFont)

        # So it must PASS the check:
        assert_PASS(check(font_meta, font_fnames),
                    f"with a good font ({fontfile})...")

        # And fail if it finds a bad filename:
        font_meta.post_script_name = "WrongPSName"
        assert_results_contain(check(font_meta, font_fnames),
                               FAIL, 'mismatch',
                               f'with a bad font ({fontfile})...')


def test_check_metadata_valid_copyright():
    """ Copyright notice on METADATA.pb matches canonical pattern ? """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_valid_copyright as check,
                family_metadata,
                font_metadata)

    # Our reference Cabin Regular is known to be bad
    # Since it provides an email instead of a git URL:
    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must FAIL the check:
    assert_results_contain(check(font_meta),
                           FAIL, 'bad-notice-format',
                           'with a bad copyright notice string...')

    # Then we change it into a good string (example extracted from Archivo Black):
    # note: the check does not actually verify that the project name is correct.
    #       It only focuses on the string format.
    good_string = ("Copyright 2017 The Archivo Black Project Authors"
                   " (https://github.com/Omnibus-Type/ArchivoBlack)")
    font_meta.copyright = good_string
    assert_PASS(check(font_meta),
                'with a good copyright notice string...')

    # We also ignore case, so these should also PASS:
    font_meta.copyright = good_string.upper()
    assert_PASS(check(font_meta),
                'with all uppercase...')

    font_meta.copyright = good_string.lower()
    assert_PASS(check(font_meta),
                'with all lowercase...')


def test_check_font_copyright():
    """Copyright notices match canonical pattern in fonts"""
    from fontbakery.profiles.googlefonts import com_google_fonts_check_font_copyright as check
    # Our reference Cabin Regular is known to be bad
    # Since it provides an email instead of a git URL:
    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(fontfile)

    # So it must FAIL the check:
    assert_results_contain(check(ttFont),
                           FAIL, 'bad-notice-format',
                           'with a bad copyright notice string...')

    # Then we change it into a good string (example extracted from Archivo Black):
    # note: the check does not actually verify that the project name is correct.
    #       It only focuses on the string format.
    good_string = ("Copyright 2017 The Archivo Black Project Authors"
                   " (https://github.com/Omnibus-Type/ArchivoBlack)")
    for i, entry in enumerate(ttFont['name'].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont['name'].names[i].string = good_string.encode(entry.getEncoding())
    assert_PASS(check(ttFont),
                'with good strings...')


def test_check_metadata_reserved_font_name():
    """ Copyright notice on METADATA.pb should not contain Reserved Font Name. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_reserved_font_name as check,
                family_metadata,
                font_metadata)

    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    assert_PASS(check(font_meta),
                'with a good copyright notice string...')

    # Then we make it bad:
    font_meta.copyright += "Reserved Font Name"

    assert_results_contain(check(font_meta),
                           WARN, 'rfn',
                           'with a notice containing "Reserved Font Name"...')


def test_check_metadata_copyright_max_length():
    """ METADATA.pb: Copyright notice shouldn't exceed 500 chars. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_copyright_max_length as check,
                family_metadata,
                font_metadata)

    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    font_meta.copyright = 500 * "x"
    assert_PASS(check(font_meta),
                'with a 500-char copyright notice string...')

    font_meta.copyright = 501 * "x"
    assert_results_contain(check(font_meta),
                           FAIL, 'max-length',
                           'with a 501-char copyright notice string...')


def test_check_metadata_filenames():
    """ METADATA.pb: Font filenames match font.filename entries? """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_filenames as check,
                                                 family_metadata)
    family_dir = portable_path('data/test/montserrat/')
    family_meta = family_metadata(family_dir)

    # test PASS:
    fonts = montserrat_fonts
    assert_PASS(check(fonts, family_dir, family_meta),
                'with matching list of font files...')

    # make sure missing files are detected by the check:
    fonts = montserrat_fonts
    original_name = fonts[0]
    os.rename(original_name, "font.tmp") # rename one font file in order to trigger the FAIL
    assert_results_contain(check(fonts, family_dir, family_meta),
                           FAIL, 'file-not-found',
                           'with missing font files...')
    os.rename("font.tmp", original_name) # restore filename


    family_dir = portable_path('data/test/cabin/')
    family_meta = family_metadata(family_dir)

    # From all TTFs in Cabin's directory, the condensed ones are not
    # listed on METADATA.pb, so the check must FAIL, even if we do not
    # explicitely include them in the set of files to be checked:
    assert_results_contain(check(cabin_fonts,
                                 family_dir,
                                 family_meta),
                           FAIL, 'file-not-declared',
                           'with some font files not declared...')


def test_check_metadata_italic_style():
    """ METADATA.pb font.style "italic" matches font internals ? """
    from fontbakery.constants import MacStyle
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_italic_style as check,
                                                 family_metadata,
                                                 font_metadata)
    # Our reference Merriweather Italic is known to good
    fontfile = TEST_FILE("merriweather/Merriweather-Italic.ttf")
    ttFont = TTFont(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS:
    assert_PASS(check(ttFont, font_meta),
                'with a good font...')

    # now let's introduce issues on the FULL_FONT_NAME entries
    # to test the "bad-fullfont-name" codepath:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "BAD VALUE".encode(name.getEncoding())
            assert_results_contain(check(ttFont, font_meta),
                                   FAIL, 'bad-fullfont-name',
                                   'with a bad NameID.FULL_FONT_NAME entry...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup

    # And, finally, let's flip off that italic bit
    # and get a "bad-macstyle" FAIL (so much fun!):
    ttFont['head'].macStyle &= ~MacStyle.ITALIC
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'bad-macstyle',
                           'with bad macstyle bit value...')


def test_check_metadata_normal_style():
    """ METADATA.pb font.style "normal" matches font internals ? """
    from fontbakery.constants import MacStyle
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_normal_style as check,
                                                 family_metadata,
                                                 font_metadata)
    # This one is pretty similar to check/metadata/italic_style
    # You may want to take a quick look above...

    # Our reference Merriweather Regular is known to be good here.
    fontfile = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    ttFont = TTFont(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    assert_PASS(check(ttFont, font_meta),
                'with a good font...')

    # now we sadically insert brokenness into
    # each occurrence of the FONT_FAMILY_NAME nameid:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "Merriweather-Italic".encode(name.getEncoding())
            assert_results_contain(check(ttFont, font_meta),
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
            assert_results_contain(check(ttFont, font_meta),
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
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'bad-macstyle',
                           'with bad macstyle bit value...')


def test_check_metadata_nameid_family_and_full_names():
    """ METADATA.pb font.name and font.full_name fields match the values declared on the name table? """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_nameid_family_and_full_names as check,
                family_metadata,
                font_metadata)

    # Our reference Merriweather Regular is known to be good here.
    fontfile = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    ttFont = TTFont(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    assert_PASS(check(ttFont, font_meta),
                'with a good font...')

    # There we go again:
    # breaking FULL_FONT_NAME entries
    # one by one:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont['name'].names[i].string = "This is utterly wrong!".encode(name.getEncoding())
            assert_results_contain(check(ttFont, font_meta),
                                   FAIL, 'fullname-mismatch',
                                   'with a METADATA.pb / FULL_FONT_NAME mismatch...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup

    # And then we do the same with FONT_FAMILY_NAME entries:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            backup = name.string
            ttFont['name'].names[i].string = ("I'm listening to"
                                              " Wes Montgomery live 1965").encode(name.getEncoding())
            assert_results_contain(check(ttFont, font_meta),
                                   FAIL, 'familyname-mismatch',
                                   'with a METADATA.pb / FONT_FAMILY_NAME mismatch...')
            # and restore the good value:
            ttFont['name'].names[i].string = backup


def test_check_metadata_fontname_not_camel_cased():
    """ METADATA.pb: Check if fontname is not camel cased. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_fontname_not_camel_cased as check,
                family_metadata,
                font_metadata)

    # Our reference Cabin Regular is known to be good
    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    assert_PASS(check(font_meta),
                'with a good font...')

    # Then we FAIL with a CamelCased name:
    font_meta.name = "GollyGhost"
    assert_results_contain(check(font_meta),
                           FAIL, 'camelcase',
                           'with a bad font (CamelCased font name)...')

    # And we also make sure the check PASSes with a few known good names:
    good_names = ["VT323", "PT Sans", "Amatic SC"]
    for good_name in good_names:
        font_meta.name = good_name
        assert_PASS(check(font_meta),
                    f'with a good font name "{good_name}"...')


def test_check_metadata_match_name_familyname():
    """ METADATA.pb: Check font name is the same as family name. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_match_name_familyname as check,
                family_metadata,
                font_metadata)

    # Our reference Cabin Regular is known to be good
    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    assert_PASS(check(family_meta, font_meta),
                'with a good font...')

    # Then we FAIL with mismatching names:
    family_meta.name = "Some Fontname"
    font_meta.name = "Something Else"
    assert_results_contain(check(family_meta, font_meta),
                           FAIL, 'mismatch',
                           'with a bad font...')


def test_check_check_metadata_canonical_weight_value():
    """ METADATA.pb: Check that font weight has a canonical value. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_canonical_weight_value as check,
                family_metadata,
                font_metadata)

    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    for w in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
        font_meta.weight = w
        assert_PASS(check(font_meta),
                    f'with a good weight value ({w})...')

    for w in [150, 250, 350, 450, 550, 650, 750, 850]:
        font_meta.weight = w
        assert_results_contain(check(font_meta),
                               FAIL, 'bad-weight',
                               'with a bad weight value ({w})...')


def test_check_metadata_os2_weightclass():
    """ Checking OS/2 usWeightClass matches weight specified at METADATA.pb """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_os2_weightclass as check,
                family_metadata,
                font_metadata)

    # VF
    # Our reference Jura is known to be good
    fontfile = portable_path("data/test/varfont/jura/Jura[wght].ttf")
    ttFont = TTFont(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    assert_PASS(check(ttFont, font_meta),
                f'with a good font ({fontfile})...')

    # And fail if it finds a bad weight value:
    good_value = font_meta.weight
    bad_value = good_value + 100
    font_meta.weight = bad_value
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'mismatch',
                           f'with a bad font ({fontfile})...')

    # Static
    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        ttFont = TTFont(fontfile)
        family_directory = os.path.dirname(fontfile)
        family_meta = family_metadata(family_directory)
        font_meta = font_metadata(family_meta, fontfile)

        # So it must PASS the check:
        assert_PASS(check(ttFont, font_meta),
                    f'with a good font ({fontfile})...')

        # And fail if it finds a bad weight value:
        good_value = font_meta.weight
        bad_value = good_value + 50
        font_meta.weight = bad_value
        assert_results_contain(check(ttFont, font_meta),
                               FAIL, 'mismatch',
                               f'with a bad font ({fontfile})...')

        # If font is Thin or ExtraLight, ensure that this check can
        # accept both 100, 250 for Thin and 200, 275 for ExtraLight
        font_meta.weight = good_value
        font_meta = font_metadata(family_meta, fontfile)
        if "Thin" in fontfile:
            ttFont["OS/2"].usWeightClass = 100
            assert_PASS(check(ttFont, font_meta),
                        f'with a good font ({fontfile})...')

            ttFont["OS/2"].usWeightClass = 250
            assert_PASS(check(ttFont, font_meta),
                        f'with a good font ({fontfile})...')

        if "ExtraLight" in fontfile:
            ttFont["OS/2"].usWeightClass = 200
            assert_PASS(check(ttFont, font_meta),
                        f'with a good font ({fontfile})...')

            ttFont["OS/2"].usWeightClass = 275
            assert_PASS(check(ttFont, font_meta),
                        f'with a good font ({fontfile})...')


def NOT_IMPLEMENTED_test_check_metadata_match_weight_postscript():
    """ METADATA.pb: Metadata weight matches postScriptName. """
    # from fontbakery.profiles.googlefonts \
    #     import com_google_fonts_check_metadata_match_weight_postscript as check
    #
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "METADATA.pb: Font weight value is invalid."
    # - FAIL, "METADATA.pb: Mismatch between postScriptName and weight value."
    # - PASS


def NOT_IMPLEMENTED_test_check_metadata_canonical_style_names():
    """ METADATA.pb: Font styles are named canonically? """
    # from fontbakery.profiles.googlefonts \
    #     import com_google_fonts_check_metadata_canonical_style_names as check
    #
    # TODO: Implement-me!
    #
    # code-paths:
    # - SKIP		"Applicable only to font styles declared as 'italic' or 'normal' on METADATA.pb."
    # - FAIL, "italic"	"Font style should be italic."
    # - FAIL, "normal"	"Font style should be normal."
    # - PASS		"Font styles are named canonically."


def test_check_unitsperem_strict():
    """ Stricter unitsPerEm criteria for Google Fonts. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_unitsperem_strict as check

    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(fontfile)

    PASS_VALUES = [16, 32, 64, 128, 256, 512, 1024] # Good for better performance on legacy renderers
    PASS_VALUES.extend([500, 1000]) # or common typical values
    PASS_VALUES.extend([2000, 2048]) # not so common, but still ok

    WARN_LARGE_VALUES = [2500, 4000, 4096] # uncommon and large,
                                           # but we've seen legitimate cases such as the
                                           # Big Shoulders Family which uses 4000 since it needs more details.

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
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_version_bump as check
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
    # from fontbakery.profiles.googlefonts \
    #     import com_google_fonts_check_production_glyphs_similarity as check
    #
    # TODO: Implement-me!
    #
    # code-paths:
    # - WARN, "Following glyphs differ greatly from Google Fonts version"
    # - PASS, "Glyphs are similar"


def NOT_IMPLEMENTED_test_check_fsselection():
    """ Checking OS/2 fsSelection value. """
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_fsselection as check
    # TODO: Implement-me!
    #
    # code-paths:
    # ...


def test_check_italic_angle():
    """ Checking post.italicAngle value. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_italic_angle as check

    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(fontfile)

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
            assert_results_contain(check(ttFont, style),
                                   expected_result,
                                   expected_msg,
                                   f"with italic-angle:{value} style:{style}...")
        else:
            assert_PASS(check(ttFont, style),
                        f'with italic-angle:{value} style:{style}...')


def test_check_mac_style():
    """ Checking head.macStyle value. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_mac_style as check
    from fontbakery.constants import MacStyle

    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(fontfile)

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
        results = check(ttFont, style)

        if expected == PASS:
            assert_PASS(results,
                        'with macStyle:{macStyle_value} style:{style}...')
        else:
            assert_results_contain(results,
                                   FAIL, expected,
                                   f"with macStyle:{macStyle_value} style:{style}...")


def test_check_contour_count(montserrat_ttFonts):
    """Check glyphs contain the recommended contour count"""
    from fontbakery.profiles.googlefonts import com_google_fonts_check_contour_count as check

    # TODO: FAIL, "lacks-cmap"


    for ttFont in montserrat_ttFonts:
        assert_PASS(check(ttFont),
                    'Montserrat which was used to assemble the glyph data...')

    # Lets swap the glyf 'a' (2 contours) with glyf 'c' (1 contour)
    for ttFont in montserrat_ttFonts:
        ttFont['glyf']['a'] = ttFont['glyf']['c']
        assert_results_contain(check(ttFont),
                               WARN, 'contour-count')

# FIXME!
# Temporarily disabled since GFonts hosted Cabin files seem to have changed in ways
# that break some of the assumptions in the code-test below.
# More info at https://github.com/googlefonts/fontbakery/issues/2581
def DISABLED_test_check_production_encoded_glyphs(cabin_ttFonts):
    """Check glyphs are not missing when compared to version on fonts.google.com"""
    from fontbakery.profiles.shared_conditions import family_directory
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_production_encoded_glyphs as check,
                api_gfonts_ttFont,
                style,
                remote_styles,
                family_metadata)

    family_meta = family_metadata(family_directory(cabin_fonts[0]))
    remote = remote_styles(family_meta.name)
    if remote:
        for font in cabin_fonts:
            ttFont = TTFont(font)
            gfont = api_gfonts_ttFont(style(font), remote)

            # Cabin font hosted on fonts.google.com contains
            # all the glyphs for the font in data/test/cabin
            assert_PASS(check(ttFont, gfont),
                        f"with '{font}'")

            # Take A glyph out of font
            ttFont['cmap'].getcmap(3, 1).cmap.pop(ord('A'))
            ttFont['glyf'].glyphs.pop('A')
            assert_results_contain(check(ttFont, gfont),
                                   FAIL, 'lost-glyphs')
    else:
        print (f"Warning: Seems to have failed to download remote font files: {cabin_ttFonts}.")


def test_check_metadata_nameid_copyright():
    """ Copyright field for this font on METADATA.pb matches
        all copyright notice entries on the name table? """
    from fontbakery.utils import get_name_entry_strings
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_metadata_nameid_copyright as check,
                family_metadata,
                font_metadata)

    # Our reference Cabin Regular is known to be good
    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(fontfile)
    family_directory = os.path.dirname(fontfile)
    family_meta = family_metadata(family_directory)
    font_meta = font_metadata(family_meta, fontfile)

    # So it must PASS the check:
    assert_PASS(check(ttFont, font_meta),
                "with a good METADATA.pb for this font...")

    # Then we FAIL with mismatching names:
    good_value = get_name_entry_strings(ttFont, NameID.COPYRIGHT_NOTICE)[0]
    font_meta.copyright = good_value + "something bad"
    assert_results_contain(check(ttFont, font_meta),
                           FAIL, 'mismatch',
                           'with a bad METADATA.pb (with a copyright string not matching this font)...')


def test_check_metadata_category():
    """ Category field for this font on METADATA.pb is valid? """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_metadata_category as check,
                                                 family_metadata)
    # Our reference Cabin family...
    fontfile = TEST_FILE("cabin/Cabin-Regular.ttf")
    family_directory = os.path.dirname(fontfile)
    metadata = family_metadata(family_directory)
    assert metadata.category == "SANS_SERIF" # ...is known to be good ;-)

    # So it must PASS the check:
    assert_PASS(check(metadata),
                "with a good METADATA.pb...")

    # Then we report a problem with this sample of bad values:
    for bad_value in ["SAN_SERIF",
                      "MONO_SPACE",
                      "sans_serif",
                      "monospace"]:
        metadata.category = bad_value
        assert_results_contain(check(metadata),
                               FAIL, 'bad-value',
                               f'with a bad category "{bad_value}"...')

    # And we accept the good ones:
    for good_value in ["MONOSPACE",
                       "SANS_SERIF",
                       "SERIF",
                       "DISPLAY",
                       "HANDWRITING"]:
        metadata.category = good_value
        assert_PASS(check(metadata),
                    f'with "{good_value}"...')


def test_check_name_mandatory_entries():
    """ Font has all mandatory 'name' table entries ? """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_mandatory_entries as check

    # We'll check both RIBBI and non-RIBBI fonts
    # so that we cover both cases for FAIL/PASS scenarios

    #First with a RIBBI font:
    # Our reference Cabin Regular is known to be good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    style = "Regular"

    # So it must PASS the check:
    assert_PASS(check(ttFont, style),
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
        assert_results_contain(check(ttFont, style),
                               FAIL, 'missing-entry',
                               f'with a missing madatory (RIBBI) name entry (id={mandatory})...')

    #And now a non-RIBBI font:
    # Our reference Merriweather Black is known to be good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Black.ttf"))
    style = "Black"

    # So it must PASS the check:
    assert_PASS(check(ttFont, style),
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
        assert_results_contain(check(ttFont, style),
                               FAIL, 'missing-entry',
                               'with a missing madatory (non-RIBBI) name entry (id={mandatory})...')


def test_condition_familyname_with_spaces():
    from fontbakery.profiles.googlefonts_conditions import familyname_with_spaces
    assert familyname_with_spaces("OverpassMono") == "Overpass Mono"
    assert familyname_with_spaces("BodoniModa11") == "Bodoni Moda 11"


def test_check_name_familyname():
    """ Check name table: FONT_FAMILY_NAME entries. """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_name_familyname as check,
                                                 familyname,
                                                 familyname_with_spaces,
                                                 style)
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
        (FAIL, "mismatch", TEST_FILE("merriweather/Merriweather-LightItalic.ttf"), "Merriweather",  "Merriweather Light Italic")
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
        assert_results_contain(check(ttFont,
                                     style(filename),
                                     familyname_with_spaces(familyname(filename))),
                                     expected, keyword,
                                     f'with filename="{filename}",'
                                     f' value="{value}", style="{style(filename)}"...')


def test_check_name_subfamilyname():
    """ Check name table: FONT_SUBFAMILY_NAME entries. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_subfamilyname as check
    from fontbakery.profiles.googlefonts_conditions import expected_style

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

        style = expected_style(ttFont)
        assert_PASS(check(ttFont, expected_style(ttFont)),
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
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'bad-familyname')

    # Repeat this for a Win subfamily name
    ttFont = TTFont(filename)
    ttFont["name"].setName("Not a proper style",
                           NameID.FONT_SUBFAMILY_NAME,
                           PlatformID.WINDOWS,
                           WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'bad-familyname')


def test_check_name_fullfontname():
    """ Check name table: FULL_FONT_NAME entries. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_fullfontname as check

    # Our reference Cabin Regular is known to be good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont, "Regular", "Cabin"),
                "with a good Regular font...")

    # Let's now test the Regular exception
    # ('Regular' can be optionally ommited on the FULL_FONT_NAME entry):
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont["name"].names[index].string = "Cabin".encode(name.getEncoding())
            assert_results_contain(check(ttFont, "Regular", "Cabin"),
                                   WARN, 'lacks-regular',
                                   'with a good Regular font that omits "Regular" on FULL_FONT_NAME...')
            # restore it:
            ttFont["name"].names[index].string = backup

    # Let's also make sure our good reference Cabin BoldItalic PASSes the check.
    # This also tests the splitting of filename infered style with a space char
    ttFont = TTFont(TEST_FILE("cabin/Cabin-BoldItalic.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont, "Bold Italic", "Cabin"),
                "with a good Bold Italic font...")

    # And here we test the FAIL codepath:
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont["name"].names[index].string = "MAKE IT FAIL".encode(name.getEncoding())
            assert_results_contain(check(ttFont, "Bold Italic", "Cabin"),
                                   FAIL, 'bad-entry',
                                   'with a bad FULL_FONT_NAME entry...')
            # restore it:
            ttFont["name"].names[index].string = backup


def NOT_IMPLEMENTED_test_check_name_postscriptname():
    """ Check name table: POSTSCRIPT_NAME entries. """
    # from fontbakery.profiles.googlefonts import com_google_fonts_check_name_postscriptname as check
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "bad-entry"
    # - PASS


def test_check_name_typographicfamilyname():
    """ Check name table: TYPOGRAPHIC_FAMILY_NAME entries. """
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_name_typographicfamilyname as check,
                style,
                familyname,
                familyname_with_spaces)

    # RIBBI fonts must not have a TYPOGRAPHIC_FAMILY_NAME entry
    font = TEST_FILE("montserrat/Montserrat-BoldItalic.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont,
                      style(font),
                      familyname_with_spaces(familyname(font))),
                f"with a RIBBI without nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...")

    # so we add one and make sure is emits a FAIL:
    ttFont['name'].names[5].nameID = NameID.TYPOGRAPHIC_FAMILY_NAME # 5 is arbitrary here
    assert_results_contain(check(ttFont,
                                 style(font),
                                 familyname_with_spaces(familyname(font))),
                           FAIL, 'ribbi',
                           f'with a RIBBI that has got a nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...')

    # non-RIBBI fonts must have a TYPOGRAPHIC_FAMILY_NAME entry
    font = TEST_FILE("montserrat/Montserrat-ExtraLight.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont,
                style(font),
                familyname_with_spaces(familyname(font))),
                f"with a non-RIBBI containing a nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...")

    # set bad values on all TYPOGRAPHIC_FAMILY_NAME entries:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
            ttFont['name'].names[i].string = "foo".encode(name.getEncoding())

    assert_results_contain(check(ttFont,
                                 style(font),
                                 familyname_with_spaces(familyname(font))),
                           FAIL, 'non-ribbi-bad-value',
                           'with a non-RIBBI with bad nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entries...')

    # remove all TYPOGRAPHIC_FAMILY_NAME entries
    # by changing their nameid to something else:
    for i, name in enumerate(ttFont['name'].names):
        if name.nameID == NameID.TYPOGRAPHIC_FAMILY_NAME:
            ttFont['name'].names[i].nameID = 255 # blah! :-)

    assert_results_contain(check(ttFont,
                                 style(font),
                                 familyname_with_spaces(familyname(font))),
                           FAIL, 'non-ribbi-lacks-entry',
                           f'with a non-RIBBI lacking a nameid={NameID.TYPOGRAPHIC_FAMILY_NAME} entry...')


def test_check_name_typographicsubfamilyname():
    """ Check name table: TYPOGRAPHIC_SUBFAMILY_NAME entries. """
    from fontbakery.profiles.googlefonts_conditions import expected_style
    from fontbakery.profiles.googlefonts \
        import com_google_fonts_check_name_typographicsubfamilyname as check

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
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'mismatch',
                           f'with a RIBBI that has got incorrect'
                           f' nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entries...')
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'bad-win-name')
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'bad-mac-name')

    # non-RIBBI fonts must have a TYPOGRAPHIC_SUBFAMILY_NAME entry
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    assert_PASS(check(ttFont,
                      expected_style(ttFont)),
                f'with a non-RIBBI containing a nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entry...')

    # set bad values on the win TYPOGRAPHIC_SUBFAMILY_NAME entry:
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    ttFont['name'].setName("Generic subfamily name",
                           NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                           PlatformID.WINDOWS,
                           WindowsEncodingID.UNICODE_BMP,
                           WindowsLanguageID.ENGLISH_USA)
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'bad-typo-win',
                           f'with a non-RIBBI with bad nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entries...')

    # set bad values on the mac TYPOGRAPHIC_SUBFAMILY_NAME entry:
    ttFont = TTFont(TEST_FILE(NON_RIBBI))
    ttFont['name'].setName("Generic subfamily name",
                           NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                           PlatformID.MACINTOSH,
                           MacintoshEncodingID.ROMAN,
                           MacintoshLanguageID.ENGLISH)
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
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
    assert_results_contain(check(ttFont,
                                 expected_style(ttFont)),
                           FAIL, 'missing-typo-win',
                           f'with a non-RIBBI lacking a nameid={NameID.TYPOGRAPHIC_SUBFAMILY_NAME} entry...')
                           # note: the check must not complain
                           #       about the lack of a mac entry!


def test_check_name_copyright_length():
    """ Length of copyright notice must not exceed 500 characters. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_name_copyright_length as check

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


def test_check_fontdata_namecheck():
    """ Familyname is unique according to namecheck.fontdata.com """
    from fontbakery.profiles.googlefonts import (com_google_fonts_check_fontdata_namecheck as check,
                                                 familyname)

    # We dont FAIL because this is meant as a merely informative check
    # There may be frequent cases when fonts are being updated and thus
    # already have a public family name registered on the
    # namecheck.fontdata.com database.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(font)
    assert_results_contain(check(ttFont, familyname(font)),
                           INFO, 'name-collision',
                           'with an already used name...')

    # Here we know that FamilySans has not been (and will not be)
    # registered as a real family.
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont, familyname(font)),
                'with a unique family name...')


def test_check_fontv():
    """ Check for font-v versioning """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_fontv as check
    from fontv.libfv import FontVersion

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_results_contain(check(ttFont),
                           INFO, 'bad-format',
                           'with a font that does not follow'
                           ' the suggested font-v versioning scheme ...')

    fv = FontVersion(ttFont)
    fv.set_state_git_commit_sha1(development=True)
    version_string = fv.get_name_id5_version_string()
    for record in ttFont['name'].names:
        if record.nameID == NameID.VERSION_STRING:
            record.string = version_string
    assert_PASS(check(ttFont),
                'with one that follows the suggested scheme ...')


# Temporarily disabling this code-test since check/negative_advance_width itself
# is disabled waiting for an implementation targetting the
# actual root cause of the issue.
#
# See also comments at googlefons.py as well as at
# https://github.com/googlefonts/fontbakery/issues/1727
def disabled_test_check_negative_advance_width():
    """ Check that advance widths cannot be inferred as negative. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_negative_advance_width as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_generate_static as check

    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))
    assert_PASS(check(ttFont))

    # Removing a table to deliberately break variable font
    del ttFont['fvar']
    assert_results_contain(check(ttFont),
                           FAIL, 'varlib-mutator')


def test_check_varfont_has_HVAR():
    """ Check that variable fonts have an HVAR table. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_has_HVAR as check

    # Our reference Cabin Variable Font contains an HVAR table.
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))

    # So the check must PASS.
    assert_PASS(check(ttFont))

    # Introduce the problem by removing the HVAR table:
    del ttFont['HVAR']
    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-HVAR')


# temporarily disabled.
# See: https://github.com/googlefonts/fontbakery/issues/2118#issuecomment-432283698
def DISABLED_test_check_varfont_has_MVAR():
    """ Check that variable fonts have an MVAR table. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_has_MVAR as check

    # Our reference Cabin Variable Font contains an MVAR table.
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))

    # So the check must PASS.
    assert_PASS(check(ttFont))

    # Introduce the problem by removing the MVAR table:
    del ttFont['MVAR']
    assert_results_contain(check(ttFont),
                           FAIL, 'lacks-MVAR')


def test_check_smart_dropout():
    """ Font enables smart dropout control in "prep" table instructions? """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_smart_dropout as check

    test_font_path = TEST_FILE("nunito/Nunito-Regular.ttf")

    # - PASS, "Program at 'prep' table contains instructions enabling smart dropout control."
    test_font = TTFont(test_font_path)
    assert_PASS(check(test_font))

    # - FAIL, "Font does not contain TrueType instructions enabling
    #          smart dropout control in the 'prep' table program."
    import array
    test_font["prep"].program.bytecode = array.array('B', [0])
    assert_results_contain(check(test_font),
                           FAIL, 'lacks-smart-dropout')


def test_check_vtt_clean():
    """ There must not be VTT Talk sources in the font. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_vtt_clean as check
    from fontbakery.profiles.shared_conditions import vtt_talk_sources

    good_font = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(good_font, vtt_talk_sources(good_font)))

    bad_font = TTFont(TEST_FILE("hinting/Roboto-VF.ttf"))
    assert_results_contain(check(bad_font, vtt_talk_sources(bad_font)),
                           FAIL, 'has-vtt-sources')


def test_check_aat():
    """ Are there unwanted Apple tables ? """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_aat as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_fvar_name_entries as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_has_instances as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_weight_instances as check

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
    # from fontbakery.profiles.googlefonts \
    #     import com_google_fonts_check_family_tnum_horizontal_metrics as check
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "inconsistent-widths"
    # - PASS


def test_check_integer_ppem_if_hinted():
    """ PPEM must be an integer on hinted fonts. """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_integer_ppem_if_hinted as check

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_ligature_carets as check
    from fontbakery.profiles.shared_conditions import ligatures

    # Our reference Mada Medium is known to be bad
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    lig = ligatures(ttFont)

    # So it must emit a WARN:
    assert_results_contain(check(ttFont, lig),
                           WARN, 'lacks-caret-pos',
                           'with a bad font...')

    # And FamilySans Regular is known to be bad
    ttFont = TTFont("data/test/familysans/FamilySans-Regular.ttf")
    lig = ligatures(ttFont)

    # So it must emit a WARN:
    assert_results_contain(check(ttFont, lig),
                           WARN, 'GDEF-missing',
                           'with a bad font...')

    # TODO: test the following code-paths:
    # - WARN "incomplete-caret-pos-data"
    # - FAIL "malformed"
    # - PASS (We currently lack a reference family that PASSes this check!)


def test_check_kerning_for_non_ligated_sequences():
    """ Is there kerning info for non-ligated sequences ? """
    from fontbakery.profiles.googlefonts \
        import com_google_fonts_check_kerning_for_non_ligated_sequences as check
    from fontbakery.profiles.gpos import has_kerning_info
    from fontbakery.profiles.shared_conditions import ligatures

    # Our reference Mada Medium is known to be good
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    lig = ligatures(ttFont)
    has_kinfo = has_kerning_info(ttFont)

    # So it must PASS the check:
    assert_PASS(check(ttFont, lig, has_kinfo),
                'with a good font...')

    # And Merriweather Regular is known to be bad
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    lig = ligatures(ttFont)
    has_kinfo = has_kerning_info(ttFont)

    # So the check must emit a WARN in this testcase:
    assert_results_contain(check(ttFont, lig, has_kinfo),
                           WARN, 'lacks-kern-info',
                           'with a bad font...')


def test_check_family_control_chars():
    """Are any unacceptable control characters present in font files?"""
    from fontbakery.profiles.googlefonts import com_google_fonts_check_family_control_chars as check

    passing_file = TEST_FILE("bad_character_set/control_chars/"
                             "FontbakeryTesterCCGood-Regular.ttf")
    error_onebad_cc_file = TEST_FILE("bad_character_set/control_chars/"
                                     "FontbakeryTesterCCOneBad-Regular.ttf")
    error_multibad_cc_file = TEST_FILE("bad_character_set/control_chars/"
                                       "FontbakeryTesterCCMultiBad-Regular.ttf")

    # No unacceptable control characters should pass with one file
    tt = TTFont(passing_file)
    assert_PASS(check([tt]),
                'with one good font...')

    # No unacceptable control characters should pass with multiple good files
    tt = TTFont(passing_file)
    assert_PASS(check([tt, tt]),
                'with multiple good fonts...')

    # Unacceptable control chars should fail with one file x one bad char in font
    tt = TTFont(error_onebad_cc_file)
    assert_results_contain(check([tt]),
                           FAIL, 'unacceptable',
                           'with one bad font that has one bad char...')

    # Unacceptable control chars should fail with one file x multiple bad char in font
    tt = TTFont(error_multibad_cc_file)
    assert_results_contain(check([tt]),
                           FAIL, 'unacceptable',
                           'with one bad font that has multiple bad char...')

    # Unacceptable control chars should fail with multiple files x multiple bad chars in fonts
    tt1 = TTFont(error_onebad_cc_file)
    tt2 = TTFont(error_multibad_cc_file)
    assert_results_contain(check([tt1, tt2]),
                           FAIL, 'unacceptable',
                           'with multiple bad fonts that have multiple bad chars...')


def NOT_IMPLEMENTED__test_com_google_fonts_check_repo_dirname_match_nameid_1():
    """Are any unacceptable control characters present in font files?"""
    # TODO: Implement-me!
    #
    # PASS
    # FAIL, "lacks-regular"
    # FAIL, "mismatch"
    #
    #  from fontbakery.profiles.googlefonts \
    #      import com_google_fonts_check_repo_dirname_match_nameid_1 as check
    #  passing_file = TEST_FILE(".../.ttf")
    #  ttFont = TTFont(passing_file)
    #  assert_PASS(check([ttFont]),
    #              'with one good font...')


def test_check_repo_vf_has_static_fonts():
    """Check VF family dirs in google/fonts contain static fonts"""
    from fontbakery.profiles.googlefonts import com_google_fonts_check_repo_vf_has_static_fonts as check
    import tempfile
    import shutil
    # in order for this check to work, we need to mimmic the folder structure of
    # the Google Fonts repository
    with tempfile.TemporaryDirectory() as tmp_gf_dir:
        family_dir = portable_path(tmp_gf_dir + "/ofl/testfamily")
        src_family = portable_path("data/test/varfont")
        shutil.copytree(src_family, family_dir)

        assert_results_contain(check(family_dir),
                               FAIL, 'missing',
                               'for a VF family which does not has a static dir.')

        static_dir = portable_path(family_dir + "/static")
        os.mkdir(static_dir)
        assert_results_contain(check(family_dir),
                               FAIL, 'empty',
                               'for a VF family which has a static dir but no fonts in the static dir.')

        static_fonts = portable_path("data/test/cabin")
        shutil.rmtree(static_dir)
        shutil.copytree(static_fonts, static_dir)
        assert_PASS(check(family_dir),
                    'for a VF family which has a static dir and static fonts')


def test_check_repo_fb_report():
    """ A font repository should not include fontbakery report files """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_repo_fb_report as check
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmp_dir:
        family_dir = portable_path(tmp_dir)
        src_family = portable_path("data/test/varfont")
        shutil.copytree(src_family, family_dir)

        assert_PASS(check(family_dir),
                    'for a repo without Font Bakery report files.')

        assert_PASS(check(family_dir),
                    'with a json file that is not a Font Bakery report.')

        # Add a json file that is not a FB report
        open(os.path.join(family_dir, "something_else.json"), "w+").write("this is not a FB report")

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
        assert_results_contain(check(family_dir),
                               WARN, 'fb-report',
                               'with an actual snippet of a report.')


def test_check_repo_zip_files():
    """ A font repository should not include ZIP files """
    from fontbakery.profiles.googlefonts import com_google_fonts_check_repo_zip_files as check
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmp_dir:
        family_dir = portable_path(tmp_dir)
        src_family = portable_path("data/test/varfont")
        shutil.copytree(src_family, family_dir)

        assert_PASS(check(family_dir),
                    'for a repo without ZIP files.')

        for ext in ["zip", "rar", "7z"]:
            # ZIP files must be detected even if placed on subdirectories:
            filepath = os.path.join(family_dir,
                                    f"jura",
                                    f"static",
                                    f"fonts-release.{ext}")
            #create an empty file. The check won't care about the contents:
            open(filepath, "w+")
            assert_results_contain(check(family_dir),
                                   FAIL, 'zip-files',
                                   f"when a {ext} file is found.")
            # remove the file before testing the next one ;-)
            os.remove(filepath)


def test_check_vertical_metrics_regressions(cabin_ttFonts):
    from fontbakery.profiles.shared_conditions import family_directory
    from fontbakery.profiles.googlefonts \
        import (com_google_fonts_check_vertical_metrics_regressions as check,
                api_gfonts_ttFont,
                style,
                remote_styles,
                family_metadata)
    from copy import copy

    family_meta = family_metadata(family_directory(cabin_fonts[0]))
    remote = remote_styles(family_meta.name)
    if remote:
        ttFonts = [TTFont(f) for f in cabin_fonts]
        # Cabin test family should match by default
        assert_PASS(check(ttFonts, remote),
                    'with a good family...')

        ttFonts2 = copy(ttFonts)
        for ttfont in ttFonts2:
            ttfont['OS/2'].sTypoAscender = 0
        assert_results_contain(check(ttFonts2, remote),
                               FAIL, 'bad-typo-ascender',
                               'with a family which has an incorrect typoAscender...')

        # TODO:
        #   FAIL, "bad-typo-descender"
        #   FAIL, "bad-hhea-ascender"
        #   FAIL, "bad-hhea-descender"

        remote2 = copy(remote)
        for key, ttfont in remote2.items():
            ttfont["OS/2"].fsSelection = ttfont["OS/2"].fsSelection ^ 0b10000000
        assert_results_contain(check(ttFonts, remote2),
                               FAIL, None, # FIXME: This needs a message keyword!
                               'with a remote family which does not have'
                               ' typo metrics enabled and the fonts being checked'
                               ' don\'t take this fact into consideration...')

        ttFonts3 = copy(ttFonts)
        for ttfont in ttFonts3:
            ttfont["OS/2"].sTypoAscender = 1139
            ttfont["OS/2"].sTypoDescender = -314
            ttfont["hhea"].ascent = 1139
            ttfont["hhea"].descent = -314
        assert_PASS(check(ttFonts3, remote2),
                    'with a remote family which does not have typo metrics'
                    ' enabled but the checked fonts vertical metrics have been'
                    ' set so its typo and hhea metrics match the remote'
                    ' fonts win metrics.')
    #
    #else:
    #  TODO: There should be a warning message here


def test_check_cjk_vertical_metrics():
    from fontbakery.profiles.googlefonts import com_google_fonts_check_cjk_vertical_metrics as check

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


def test_check_varfont_instance_coordinates(vf_ttFont):
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_instance_coordinates as check
    from fontbakery.parse import instance_parse
    from copy import copy

    # OpenSans-Roman-VF is correct
    assert_PASS(check(vf_ttFont),
                'with a variable font which has correct instance coordinates.')

    vf_ttFont2 = copy(vf_ttFont)
    for instance in vf_ttFont2['fvar'].instances:
        for axis in instance.coordinates.keys():
            instance.coordinates[axis] = 0
    assert_results_contain(check(vf_ttFont2),
                           FAIL, None, # FIXME: This needs a message keyword
                           'with a variable font which does not have'
                           ' correct instance coordinates.')


def test_check_varfont_instance_names(vf_ttFont):
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_instance_names as check
    from fontbakery.parse import instance_parse
    from copy import copy

    assert_PASS(check(vf_ttFont),
                'with a variable font which has correct instance names.')

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
    from fontbakery.profiles.googlefonts \
        import com_google_fonts_check_varfont_duplicate_instance_names as check
    from copy import copy

    assert_PASS(check(vf_ttFont),
                'with a variable font which has unique instance names.')

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
    from fontbakery.profiles.googlefonts import com_google_fonts_check_varfont_unsupported_axes as check
    from fontbakery.profiles.shared_conditions import slnt_axis, ital_axis
    from fontTools.ttLib.tables._f_v_a_r import Axis

    # Our reference varfont, CabinVFBeta.ttf, lacks 'ital' and 'slnt' variation axes.
    # So, should pass the check:
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont))

    # If we add 'ital' it must FAIL:
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

