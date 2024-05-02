import math
import os
import shutil
import sys

import pytest
from conftest import ImportRaiser, remove_import_raiser
from fontTools.ttLib import TTFont

from fontbakery.checks.googlefonts.conditions import expected_font_names
from fontbakery.checks.googlefonts.glyphset import can_shape
from fontbakery.codetesting import (
    GLYPHSAPP_TEST_FILE,
    TEST_FILE,
    CheckTester,
    MockFont,
    assert_PASS,
    assert_results_contain,
    assert_SKIP,
    portable_path,
    MockContext,
)
from fontbakery.constants import (
    OFL_BODY_TEXT,
    MacintoshEncodingID,
    MacintoshLanguageID,
    NameID,
    PlatformID,
    WindowsEncodingID,
    WindowsLanguageID,
)
from fontbakery.profiles import googlefonts as googlefonts_profile
from fontbakery.status import DEBUG, ERROR, FAIL, FATAL, INFO, PASS, SKIP, WARN
from fontbakery.testable import Font

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

OVERRIDE_SUFFIX = ""

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
    TEST_FILE("cabin/Cabin-SemiBold.ttf"),
]

cabin_condensed_fonts = [
    TEST_FILE("cabincondensed/CabinCondensed-Regular.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-Medium.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-Bold.ttf"),
    TEST_FILE("cabincondensed/CabinCondensed-SemiBold.ttf"),
]

rosarivo_fonts = [
    TEST_FILE("rosarivo_metadata/Rosarivo-Italic.ttf"),
    TEST_FILE("rosarivo_metadata/Rosarivo-Regular.ttf"),
]

cjk_font = TEST_FILE("cjk/SourceHanSans-Regular.otf")


@pytest.fixture
def cabin_ttFonts():
    return [TTFont(path) for path in cabin_fonts]


@pytest.fixture
def vf_ttFont():
    path = TEST_FILE("varfont/Oswald-VF.ttf")
    return TTFont(path)


def change_name_table_id(ttFont, nameID, newEntryString, platEncID=0):
    for i, nameRecord in enumerate(ttFont["name"].names):
        if nameRecord.nameID == nameID and nameRecord.platEncID == platEncID:
            ttFont["name"].names[i].string = newEntryString


def delete_name_table_id(ttFont, nameID):
    delete = []
    for i, nameRecord in enumerate(ttFont["name"].names):
        if nameRecord.nameID == nameID:
            delete.append(i)
    for i in sorted(delete, reverse=True):
        del ttFont["name"].names[i]


@pytest.fixture
def cabin_regular_path():
    return portable_path("data/test/cabin/Cabin-Regular.ttf")


def test_extra_needed_exit_from_conditions(monkeypatch):
    module_name = "google.protobuf"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    with pytest.raises(SystemExit):
        check = CheckTester("com.google.fonts/check/metadata/designer_profiles")
        font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
        check(font)

    remove_import_raiser(module_name)


def test_extra_needed_exit(monkeypatch):
    module_name = "axisregistry"
    sys.meta_path.insert(0, ImportRaiser(module_name))
    monkeypatch.delitem(sys.modules, module_name, raising=False)

    with pytest.raises(SystemExit):
        check = CheckTester("com.google.fonts/check/canonical_filename")
        ttFont = TTFont(TEST_FILE("cabinvfbeta/Cabin-VF.ttf"))
        check(ttFont)

    remove_import_raiser(module_name)


@pytest.mark.parametrize(
    """fp,result""",
    [
        (TEST_FILE("montserrat/Montserrat-Thin.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-Light.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-Regular.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-Medium.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-SemiBold.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-Bold.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-Black.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-LightItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-Italic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"), PASS),
        (TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"), PASS),
        (TEST_FILE("cabinvfbeta/CabinVFBeta-Italic[wght].ttf"), PASS),
        (TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"), FAIL),
        (TEST_FILE("cabinvfbeta/Cabin-Italic.ttf"), FAIL),
        (TEST_FILE("cabinvfbeta/Cabin-Roman.ttf"), FAIL),
        (TEST_FILE("cabinvfbeta/Cabin-Italic-VF.ttf"), FAIL),
        (TEST_FILE("cabinvfbeta/Cabin-Roman-VF.ttf"), FAIL),
        (TEST_FILE("cabinvfbeta/Cabin-VF.ttf"), FAIL),
        # axis tags are sorted
        (TEST_FILE("cabinvfbeta/CabinVFBeta[wdth,wght].ttf"), PASS),
        # axis tags are NOT sorted
        (TEST_FILE("cabinvfbeta/CabinVFBeta[wght,wdth].ttf"), FAIL),
    ],
)
def test_check_canonical_filename(fp, result):
    """Files are named canonically."""
    check = CheckTester("com.google.fonts/check/canonical_filename")
    ttFont = TTFont(fp)

    if result == PASS:
        assert_PASS(check(ttFont), f'with "{ttFont.reader.file.name}" ...')
    else:
        assert_results_contain(
            check(ttFont), FAIL, "bad-filename", f'with "{ttFont.reader.file.name}" ...'
        )


def test_check_description_broken_links():
    """Does DESCRIPTION file contain broken links ?"""
    check = CheckTester("com.google.fonts/check/description/broken_links")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with description file that has no links...")

    good_desc = Font(font).description
    good_desc += (
        "<a href='http://example.com'>Good Link</a>"
        "<a href='http://fonts.google.com'>Another Good One</a>"
    )

    assert_PASS(
        check(MockFont(file=font, description=good_desc)),
        "with description file that has good links...",
    )

    bad_desc = (
        good_desc + "<a href='mailto:juca@members.fsf.org'>An example mailto link</a>"
    )
    assert_results_contain(
        check(MockFont(file=font, description=bad_desc)),
        FAIL,
        "email",
        'with a description file containing "mailto" links...',
    )

    bad_desc = (
        good_desc
        + "<a href='http://thisisanexampleofabrokenurl.com/'>This is a Bad Link</a>"
    )
    assert_results_contain(
        check(MockFont(file=font, description=bad_desc)),
        FAIL,
        "broken-links",
        "with a description file containing a known-bad URL...",
    )

    # TODO: WARN, 'timeout'


def test_check_description_git_url():
    """Does DESCRIPTION file contain an upstream Git repo URL?"""
    check = CheckTester("com.google.fonts/check/description/git_url")

    # TODO: test INFO 'url-found'

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(
        check(font),
        FAIL,
        "lacks-git-url",
        "with description file that has no git repo URLs...",
    )

    good_desc = (
        "<a href='https://github.com/uswds/public-sans'>Good URL</a>"
        "<a href='https://gitlab.com/smc/fonts/uroob'>Another Good One</a>"
    )
    assert_PASS(
        check(
            MockFont(file=TEST_FILE("cabin/Cabin-Regular.ttf"), description=good_desc)
        ),
        "with description file that has good links...",
    )

    bad_desc = "<a href='https://v2.designsystem.digital.gov'>Bad URL</a>"
    assert_results_contain(
        check(
            MockFont(file=TEST_FILE("cabin/Cabin-Regular.ttf"), description=bad_desc)
        ),
        FAIL,
        "lacks-git-url",
        "with description file that has false git in URL...",
    )


def test_check_description_valid_html():
    """DESCRIPTION file is a propper HTML snippet ?"""
    check = CheckTester("com.google.fonts/check/description/valid_html")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(
        check(font), "with description file that contains a good HTML snippet..."
    )

    bad_desc = open(TEST_FILE("cabin/FONTLOG.txt"), "r", encoding="utf-8").read()
    assert_results_contain(
        check(MockFont(file=font, description=bad_desc)),
        FAIL,
        "lacks-paragraph",
        "with a known-bad file (without HTML paragraph tags)...",
    )

    bad_desc = "<html>foo</html>"
    assert_results_contain(
        check(MockFont(file=font, description=bad_desc)),
        FAIL,
        "html-tag",
        "with description file that contains the <html> tag...",
    )

    good_desc = (
        "<p>This example has the & caracter,"
        " and does not escape it with an HTML entity code."
        " It could use &amp; instead, but that's not strictly necessary."
        "</p>"
    )
    # See discussion at https://github.com/fonttools/fontbakery/issues/3840
    assert_PASS(
        check(MockFont(file=font, description=good_desc)),
        "with a file containing ampersand char without HTML entity syntax...",
    )


def test_check_description_min_length():
    """DESCRIPTION.en_us.html must have more than 200 bytes."""
    check = CheckTester("com.google.fonts/check/description/min_length")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    bad_length = "a" * 199
    assert_results_contain(
        check(MockFont(file=font, description=bad_length)),
        FAIL,
        "too-short",
        "with 199-byte buffer...",
    )

    bad_length = "a" * 200
    assert_results_contain(
        check(MockFont(file=font, description=bad_length)),
        FAIL,
        "too-short",
        "with 200-byte buffer...",
    )

    good_length = "a" * 201
    assert_PASS(
        check(MockFont(file=font, description=good_length)), "with 201-byte buffer..."
    )


def test_check_description_eof_linebreak():
    """DESCRIPTION.en_us.html should end in a linebreak."""
    check = CheckTester("com.google.fonts/check/description/eof_linebreak")

    font = TEST_FILE("nunito/Nunito-Regular.ttf")

    bad = (
        "We want to avoid description files\n"
        "without an end-of-file linebreak\n"
        "like this one."
    )
    assert_results_contain(
        check(MockFont(file=font, description=bad)),
        WARN,
        "missing-eof-linebreak",
        "when we lack an end-of-file linebreak...",
    )

    good = "On the other hand, this one\nis good enough.\n"
    assert_PASS(check(MockFont(file=font, description=good)), "when we add one...")


def test_check_name_family_and_style_max_length():
    """Name table entries should not be too long."""
    check = CheckTester("com.google.fonts/check/name/family_and_style_max_length")

    # Our reference Cabin Regular is known to be good
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # Then we emit a FAIL with long family/style names
    # See https://github.com/fonttools/fontbakery/issues/2179 for
    # a discussion of the requirements

    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            # This has 33 chars, while the max currently allowed is 32
            bad = "An Absurdly Long Family Name Font"
            assert len(bad) == 33
            ttFont["name"].names[index].string = bad.encode(name.getEncoding())
        if name.nameID == NameID.POSTSCRIPT_NAME:
            bad = "AbsurdlyLongFontName-Regular"
            assert len(bad) == 28
            ttFont["name"].names[index].string = bad.encode(name.getEncoding())

    results = check(ttFont)
    assert_results_contain(results, FAIL, "nameid4-too-long", "with a bad font...")
    assert_results_contain(results, WARN, "nameid6-too-long", "with a bad font...")

    # Restore the original VF
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # ...and break the check again with a bad fvar instance name:
    nameid_to_break = ttFont["fvar"].instances[0].subfamilyNameID
    for index, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            assert len(ttFont["name"].names[index].string) + 28 > 32
        if name.nameID == nameid_to_break:
            bad = "WithAVeryLongAndBadStyleName"
            assert len(bad) == 28
            ttFont["name"].names[index].string = bad.encode(name.getEncoding())
            break
    assert_results_contain(
        check(ttFont), FAIL, "instance-too-long", "with a bad font..."
    )


def DISABLED_test_check_glyphs_file_name_family_and_style_max_length():
    """Combined length of family and style must not exceed 27 characters."""
    check = CheckTester(
        googlefonts_profile,
        "com.google.fonts/check/glyphs_file/name/family_and_style_max_length",
    )

    # Our reference Comfortaa.glyphs is known to be good
    glyphsFile = GLYPHSAPP_TEST_FILE("Comfortaa.glyphs")

    # So it must PASS the check:
    assert_PASS(check(glyphsFile), "with a good font...")

    # Then we emit a WARNing with long family/style names
    # Originaly these were based on the example on the glyphs tutorial
    # (at https://glyphsapp.com/tutorials/multiple-masters-part-3-setting-up-instances)
    # but later we increased a bit the max allowed length.

    # First we expect a WARN with a bad FAMILY NAME
    # This has 28 chars, while the max currently allowed is 27.
    bad = "AnAbsurdlyLongFamilyNameFont"
    assert len(bad) == 28
    glyphsFile.familyName = bad
    assert_results_contain(
        check(glyphsFile), WARN, "too-long", "with a too long font familyname..."
    )

    for i in range(len(glyphsFile.instances)):
        # Restore the good glyphs file...
        glyphsFile = GLYPHSAPP_TEST_FILE("Comfortaa.glyphs")

        # ...and break the check again with a long SUBFAMILY NAME
        # on one of its instances:
        bad_stylename = "WithAVeryLongAndBadStyleName"
        assert len(bad_stylename) == 28
        glyphsFile.instances[i].fullName = f"{glyphsFile.familyName} {bad_stylename}"
        assert_results_contain(
            check(glyphsFile), WARN, "too-long", "with a too long stylename..."
        )


def test_check_name_line_breaks():
    """Name table entries should not contain line-breaks."""
    check = CheckTester("com.google.fonts/check/name/line_breaks")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    num_entries = len(ttFont["name"].names)
    for i in range(num_entries):
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        encoding = ttFont["name"].names[i].getEncoding()
        ttFont["name"].names[i].string = "bad\nstring".encode(encoding)
        assert_results_contain(
            check(ttFont),
            FAIL,
            "line-break",
            f"with name entries containing a linebreak ({i}/{num_entries})...",
        )


def test_check_name_rfn():
    """Name table strings must not contain 'Reserved Font Name'."""
    check = CheckTester("com.google.fonts/check/name/rfn")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # The OFL text contains the term 'Reserved Font Name',
    # which should not cause a FAIL:
    ttFont["name"].setName(
        OFL_BODY_TEXT,
        NameID.LICENSE_DESCRIPTION,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    assert_PASS(check(ttFont), "with the OFL full text...")

    # NOTE: This is not a real copyright statement. It is only meant to test the check.
    with_nunito_rfn = (
        "Copyright 2022 The Nunito Project Authors"
        " (https://github.com/googlefonts/NunitoSans),"
        " with Reserved Font Name Nunito."
    )
    ttFont["name"].setName(
        with_nunito_rfn,
        NameID.VERSION_STRING,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    assert_results_contain(
        check(ttFont),
        FAIL,
        "rfn",
        'with "Reserved Font Name Nunito" on a name table entry...',
    )

    # NOTE: This is not a real copyright statement. It is only meant to test the check.
    with_other_familyname_rfn = (
        "Copyright 2022 The FooBar Project Authors"
        " (https://github.com/foo/bar),"
        " with Reserved Font Name FooBar."
    )
    ttFont["name"].setName(
        with_other_familyname_rfn,
        NameID.VERSION_STRING,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    msg = assert_results_contain(
        check(ttFont),
        WARN,
        "legacy-familyname",
        'with "Reserved Font Name" that references an older'
        " familyname not being used in this font project...",
    )
    assert "(FooBar)" in msg


def test_check_name_family_name_compliance():
    """Check family name for GF Guide compliance."""
    check = CheckTester("com.google.fonts/check/name/family_name_compliance")

    def set_name(font, nameID, string):
        for record in font["name"].names:
            if record.nameID == nameID:
                old_string = record.toUnicode()
                if string != old_string:
                    font["name"].setName(
                        string,
                        record.nameID,
                        record.platformID,
                        record.platEncID,
                        record.langID,
                    )

    # CAMEL CASE
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # FAIL with a CamelCased name:
    set_name(ttFont, 1, "GollyGhost")
    assert_results_contain(
        check(ttFont), FAIL, "camelcase", "with a bad font name (CamelCased)..."
    )
    set_name(ttFont, 1, "KonKhmer_SleokChher")
    assert_results_contain(
        check(ttFont), FAIL, "camelcase", "with a bad font name (CamelCased)..."
    )

    # PASS with a known CamelCased exception:
    set_name(ttFont, 1, "KoHo")
    assert_results_contain(
        check(ttFont),
        PASS,
        "known-camelcase-exception",
        "with a bad font name (CamelCased)...",
    )

    # ABBREVIATIONS
    set_name(ttFont, 1, "DTL Prokyon")
    assert_results_contain(check(ttFont), FAIL, "abbreviation", "with a bad font name")
    set_name(ttFont, 1, "PT Sans")
    assert_results_contain(
        check(ttFont), PASS, "known-abbreviation-exception", "with a bad font name"
    )
    # Allow SC ending
    set_name(ttFont, 1, "Amatic SC")
    assert_PASS(check(ttFont), "with a good font...")

    # FORBIDDEN CHARACTERS
    set_name(ttFont, 1, "KonKhmer_SleokChher")
    message = assert_results_contain(
        check(ttFont), FAIL, "forbidden-characters", "with a bad font name"
    )
    assert message == (
        '"KonKhmer_SleokChher" contains the following characters'
        ' which are not allowed: "_".'
    )
    set_name(ttFont, 1, "Kon*Khmer_Sleok-Chher")
    message = assert_results_contain(
        check(ttFont), FAIL, "forbidden-characters", "with a bad font name"
    )
    assert message == (
        '"Kon*Khmer_Sleok-Chher" contains the following characters'
        ' which are not allowed: "*-_".'
    )

    # STARTS WITH UPPERCASE
    set_name(ttFont, 1, "cabin")
    message = assert_results_contain(
        check(ttFont), FAIL, "starts-with-not-uppercase", "with a bad font name"
    )

    # # And we also make sure the check PASSes with a few known good names:
    set_name(ttFont, 1, "VT323")
    assert_PASS(check(ttFont), "with a good font...")


def test_check_metadata_parses():
    """Check METADATA.pb parse correctly."""
    check = CheckTester("com.google.fonts/check/metadata/parses")

    good = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    assert_PASS(check(good), "with a good METADATA.pb file...")

    skip = MockFont(file=TEST_FILE("slabo/Slabo-Regular.ttf"))
    assert_results_contain(
        check(skip), SKIP, "file-not-found", "with a missing METADATA.pb file..."
    )

    bad = MockFont(file=TEST_FILE("broken_metadata/foo.ttf"))
    assert_results_contain(
        check(bad), FATAL, "parsing-error", "with a bad METADATA.pb file..."
    )


def test_check_metadata_designer_values():
    """Multiple values in font designer field in
    METADATA.pb must be separated by commas."""
    check = CheckTester("com.google.fonts/check/metadata/designer_values")

    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    assert_PASS(check(font), "with a good METADATA.pb file...")

    md = Font(font).family_metadata
    md.designer = "Pentagram, MCKL"
    assert_PASS(
        check(MockFont(file=font, family_metadata=md)),
        "with a good multiple-designers string...",
    )

    md.designer = "Pentagram / MCKL"  # This actually happened on an
    # early version of the Red Hat Text family
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "slash",
        "with a bad multiple-designers string (names separated by a slash char)...",
    )


def test_check_metadata_broken_links():
    """Does DESCRIPTION file contain broken links?"""
    # check = CheckTester("com.google.fonts/check/metadata/broken_links")
    # TODO: Implement-me!
    # FAIL, "email"
    # WARN, "timeout"
    # FAIL, "broken-links"


def test_check_metadata_undeclared_fonts():
    """Ensure METADATA.pb lists all font binaries."""
    check = CheckTester("com.google.fonts/check/metadata/undeclared_fonts")

    # Our reference Nunito family is know to be good here.
    font = TEST_FILE("nunito/Nunito-Regular.ttf")
    assert_PASS(check(font))

    # Our reference Cabin family has files that are not declared in its METADATA.pb:
    # - CabinCondensed-Medium.ttf
    # - CabinCondensed-SemiBold.ttf
    # - CabinCondensed-Regular.ttf
    # - CabinCondensed-Bold.ttf
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(check(font), FAIL, "file-not-declared")

    # We placed an additional file on a subdirectory of our reference
    # OverpassMono family with the name "another_directory/ThisShouldNotBeHere.otf"
    font = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_results_contain(check(font), WARN, "font-on-subdir")

    # We do accept statics folder though!
    # Jura is an example:
    font = TEST_FILE("varfont/jura/Jura[wght].ttf")
    assert_PASS(check(font))


def test_check_family_equal_codepoint_coverage(mada_ttFonts, cabin_ttFonts):
    """Fonts have equal codepoint coverage?"""
    check = CheckTester("com.google.fonts/check/family/equal_codepoint_coverage")

    # our reference Cabin family is know to be good here.
    assert_PASS(check(cabin_ttFonts), "with a good family.")

    # Let's de-encode some glyphs
    del cabin_ttFonts[1]["cmap"].tables[0].cmap[8730]
    assert_results_contain(
        check(cabin_ttFonts),
        FAIL,
        "glyphset-diverges",
        "with fonts that diverge.",
    )


def test_check_fstype():
    """Checking OS/2 fsType"""
    check = CheckTester("com.google.fonts/check/fstype")

    # our reference Cabin family is know to be good here.
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font without DRM.")

    # modify the OS/2 fsType value to something different than zero:
    ttFont["OS/2"].fsType = 1

    assert_results_contain(
        check(ttFont),
        FAIL,
        "drm",
        "with fonts that enable DRM restrictions via non-zero fsType bits.",
    )


def test_condition_registered_vendor_ids():
    """Get a list of vendor IDs from Microsoft's website."""
    from fontbakery.checks.googlefonts.os2 import registered_vendor_ids

    registered_ids = registered_vendor_ids()

    print('As of July 2018, "MLAG": "Michael LaGattuta" must show up in the list...')
    assert "MLAG" in registered_ids  # Michael LaGattuta

    print('As of December 2020, "GOOG": "Google" must show up in the list...')
    assert "GOOG" in registered_ids  # Google

    print('"CFA ": "Computer Fonts Australia" is a good vendor id, lacking a URL')
    assert "CFA " in registered_ids  # Computer Fonts Australia

    print(
        '"GNU ": "Free Software Foundation, Inc." is a good vendor id'
        " with 3 letters and a space."
    )
    # Free Software Foundation, Inc. / http://www.gnu.org/
    assert "GNU " in registered_ids

    print('"GNU" without the right-padding space must not be on the list!')
    assert "GNU" not in registered_ids  # All vendor ids must be 4 chars long!

    print('"ADBE": "Adobe" is a good 4-letter vendor id.')
    assert "ADBE" in registered_ids  # Adobe

    print('"B&H ": "Bigelow & Holmes" is a valid vendor id that contains an ampersand.')
    assert "B&H " in registered_ids  # Bigelow & Holmes

    print(
        '"MS  ": "Microsoft Corp." is a good vendor id'
        " with 2 letters and padded with spaces."
    )
    assert "MS  " in registered_ids  # Microsoft Corp.

    print('"TT\0\0": we also accept vendor-IDs containing NULL-padding.')
    assert "TT\0\0" in registered_ids  # constains NULL bytes

    print("All vendor ids must be 4 chars long!")
    assert "GNU" not in registered_ids  # 3 chars long is bad
    assert "MS" not in registered_ids  # 2 chars long is bad
    assert "H" not in registered_ids  # 1 char long is bad

    print(
        '"H   ": "Hurme Design" is a good vendor id'
        " with a single letter padded with spaces."
    )
    assert "H   " in registered_ids  # Hurme Design

    print('"   H": But not padded on the left, please!')
    # a bad vendor id (presumably for "Hurme Design"
    # but with a vendor id parsing bug)
    assert "   H" not in registered_ids

    print('"????" is an unknown vendor id.')
    assert "????" not in registered_ids


def test_check_vendor_id():
    """Checking OS/2 achVendID"""
    check = CheckTester("com.google.fonts/check/vendor_id")

    # Let's start with our reference Merriweather Regular
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    bad_vids = ["UKWN", "ukwn", "PfEd", "PYRS"]
    for bad_vid in bad_vids:
        ttFont["OS/2"].achVendID = bad_vid
        assert_results_contain(check(ttFont), WARN, "bad", f'with bad vid "{bad_vid}".')

    ttFont["OS/2"].achVendID = None
    assert_results_contain(
        check(ttFont), WARN, "not-set", "with font missing vendor id info."
    )

    ttFont["OS/2"].achVendID = "????"
    assert_results_contain(check(ttFont), WARN, "unknown", "with unknwon vendor id.")

    # we now change the fields into a known good vendor id:
    ttFont["OS/2"].achVendID = "APPL"
    assert_PASS(check(ttFont), "with a good font.")

    # And let's also make sure it works here:
    ttFont["OS/2"].achVendID = "GOOG"
    assert_PASS(check(ttFont), "with a good font.")


def test_check_glyph_coverage():
    """Check glyph coverage."""
    check = CheckTester("com.google.fonts/check/glyph_coverage")

    # Our reference Cabin Regular is known to be bad here.
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # Deactivating this for now as GF_TransLatin_Arabic isn't available under
    # the new glyphset setup yet.
    # TODO: Reactivate this:
    # assert_results_contain(
    #     check(ttFont),
    #     WARN,
    #     "missing-codepoints",
    #     "GF_TransLatin_Arabic is almost fulfilled.",
    # )

    # Let's fix it then...
    cmap = ttFont.getBestCmap()
    cmap[0x1E34] = 0x1E34  # (LATIN CAPITAL LETTER K WITH LINE BELOW)
    cmap[0x1E35] = 0x1E35  # (LATIN SMALL LETTER K WITH LINE BELOW)
    cmap[0x1E96] = 0x1E96  # (LATIN SMALL LETTER H WITH LINE BELOW)
    cmap[0x02BD] = 0x02BD  # (MODIFIER LETTER REVERSED COMMA)
    assert_PASS(check(ttFont), "with a good font.")

    # Moirai is Korean, so only needs kernel
    ttFont = TTFont(TEST_FILE("moiraione/MoiraiOne-Regular.ttf"))
    assert 0x02C7 not in ttFont.getBestCmap()  # This is in core but not kernel
    assert_PASS(check(ttFont))


def test_check_name_unwanted_chars():
    """Substitute copyright, registered and trademark
    symbols in name table entries."""
    check = CheckTester("com.google.fonts/check/name/unwanted_chars")

    # Our reference Mada Regular is know to be bad here.
    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(check(font), FAIL, "unwanted-chars", "with a bad font...")

    # Our reference Cabin Regular is know to be good here.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")


def test_check_usweightclass():
    """Checking OS/2 usWeightClass."""
    check = CheckTester("com.google.fonts/check/usweightclass")

    # Our reference Mada Regular is know to be bad here.
    font = TEST_FILE("mada/Mada-Regular.ttf")
    ttFont = TTFont(font)
    assert_results_contain(
        check(ttFont), FAIL, "bad-value", f'with bad font "{font}" ...'
    )

    # All fonts in our reference Cabin family are know to be good here.
    for font in cabin_fonts:
        ttFont = TTFont(font)
        assert_PASS(check(ttFont), f'with good font "{font}"...')

    # Check otf Thin == 250 and ExtraLight == 275
    font = TEST_FILE("rokkitt/Rokkitt-Thin.otf")
    ttFont = TTFont(font)
    assert_results_contain(
        check(ttFont), FAIL, "bad-value", f'with bad font "{font}"...'
    )

    ttFont["OS/2"].usWeightClass = 250
    assert_PASS(check(ttFont), f'with good font "{font}" (usWeightClass = 250) ...')

    font = TEST_FILE("rokkitt/Rokkitt-ExtraLight.otf")
    ttFont = TTFont(font)
    assert_results_contain(
        check(ttFont), FAIL, "bad-value", f'with bad font "{font}" ...'
    )

    ttFont["OS/2"].usWeightClass = 275
    assert_PASS(check(ttFont), f'with good font "{font}" (usWeightClass = 275) ...')

    # TODO: test italic variants to ensure we do not get regressions of
    #       this bug: https://github.com/fonttools/fontbakery/issues/2650

    # Check with VF font reported in issue:
    # https://github.com/fonttools/fontbakery/issues/4113
    font = TEST_FILE("playfair/Playfair-Italic[opsz,wdth,wght].ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont), f'with good font "{font}" (usWeightClass = 300) ...')

    ttFont["OS/2"].usWeightClass = 400
    assert_results_contain(
        check(ttFont), FAIL, "bad-value", f'with bad font "{font}"...'
    )


def test_family_directory_condition():
    assert Font("some_directory/Foo.ttf").family_directory == "some_directory"
    assert (
        Font("some_directory/subdir/Foo.ttf").family_directory
        == "some_directory/subdir"
    )
    assert (
        Font("Foo.ttf").family_directory == "."
    )  # This is meant to ensure license files
    # are correctly detected on the current
    # working directory.


def test_check_family_has_license():
    """Check font project has a license."""
    check = CheckTester("com.google.fonts/check/family/has_license")

    def licenses_for_test(path):
        found = MockFont(file=path + "/NoSuch.ttf").licenses
        # If the tests are running inside a git checkout of fontbakery,
        # FontBakery's own license will also be detected:
        # ['data/test/028/multiple/OFL.txt',
        #  'data/test/028/multiple/LICENSE.txt',
        #  '/home/dan/src/fontbakery/LICENSE.txt']
        # Filter it out so it doesn't interfere with the test.
        found = [lic for lic in found if not os.path.isabs(lic)]
        return found

    dir_path = "ofl/foo/bar"
    detected_licenses = licenses_for_test(portable_path("data/test/028/multiple"))
    assert len(detected_licenses) > 1
    assert_results_contain(
        check(MockFont(file=dir_path, licenses=detected_licenses)),
        FAIL,
        "multiple",
        "with multiple licenses...",
    )

    detected_licenses = licenses_for_test(portable_path("data/test/028/none"))
    assert_results_contain(
        check(MockFont(file=dir_path, licenses=detected_licenses)),
        FAIL,
        "no-license",
        "with no license...",
    )

    detected_licenses = licenses_for_test(portable_path("data/test/028/pass_ofl"))
    assert_PASS(
        check(MockFont(file=dir_path, licenses=detected_licenses)),
        "with a single OFL license...",
    )

    detected_licenses = licenses_for_test(portable_path("data/test/028/pass_apache"))
    assert_PASS(
        check(MockFont(file=dir_path, licenses=detected_licenses)),
        "with a single Apache license...",
    )

    msg = assert_results_contain(check([""]), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: gfonts_repo_structure" in msg


def test_check_license_ofl_copyright():
    """Check license file has good copyright string."""
    check = CheckTester("com.google.fonts/check/license/OFL_copyright")

    # And Mada has a bad copyright string format:
    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(
        check(font), FAIL, "bad-format", "with bad string formatting."
    )

    # so we fix it:
    SOME_GOOD_TEXT = (
        "Copyright 2019 The Montserrat Project Authors"
        " (https://github.com/julietaula/montserrat)"
    )
    assert_PASS(
        check(MockFont(file=font, license_contents=SOME_GOOD_TEXT)),
        "with good license contents.",
    )


def test_check_license_ofl_body_text():
    """Check OFL.txt contains correct body text."""
    check = CheckTester("com.google.fonts/check/license/OFL_body_text")

    # Our reference Montserrat family is know to have
    # a proper OFL.txt license file.
    # NOTE: This is currently considered good
    #       even though it uses an "http://" URL
    font = MockFont(file=TEST_FILE("montserrat/Montserrat-Regular.ttf"))

    assert_PASS(check(font), 'with a good OFL.txt license with "http://" url.')

    # using "https://" is also considered good:
    font.license_contents = font.license_contents.replace("http://", "https://")
    assert_PASS(
        check(font),
        'with a good OFL.txt license with "https://" url.',
    )

    # modify a tiny bit of the license text, to trigger the FAIL:
    font.license_contents = font.license_contents.replace(
        "SIL OPEN FONT LICENSE Version 1.1", "SOMETHING ELSE :-P Version Foo"
    )
    assert_results_contain(
        check(font),
        WARN,
        "incorrect-ofl-body-text",
        "with incorrect ofl body text",
    )


def test_check_name_license(mada_ttFonts):
    """Check copyright namerecords match license file."""
    check = CheckTester("com.google.fonts/check/name/license")

    # Our reference Mada family has its copyright name records properly set
    # identifying it as being licensed under the Open Font License.
    for font in mada_fonts:
        assert_PASS(check(font), "with good fonts ...")

    for font in mada_fonts:
        assert_results_contain(
            check(MockFont(file=font, license_filename="LICENSE.txt")),  # Apache
            FAIL,
            "wrong",
            "with wrong entry values ...",
        )

    for ttFont in mada_ttFonts:
        delete_name_table_id(ttFont, NameID.LICENSE_DESCRIPTION)
        assert_results_contain(
            check(ttFont), FAIL, "missing", "with missing copyright namerecords ..."
        )

    # TODO:
    # WARN, "http" / "http-in-description"


def NOT_IMPLEMENTED_test_check_name_license_url():
    """License URL matches License text on name table?"""
    # check = CheckTester( "com.google.fonts/check/name/license_url")
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
    """Description strings in the name table
    must not exceed 200 characters.
    """
    check = CheckTester("com.google.fonts/check/name/description_max_length")

    # Our reference Mada Regular is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # Here we add strings to NameID.DESCRIPTION with exactly 100 chars,
    # so it should still PASS:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.DESCRIPTION:
            ttFont["name"].names[i].string = ("a" * 200).encode(name.getEncoding())
    assert_PASS(check(ttFont), "with a 200 char string...")

    # And here we make the strings longer than 200 chars
    # in order to make the check emit a WARN:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.DESCRIPTION:
            ttFont["name"].names[i].string = ("a" * 201).encode(name.getEncoding())
    assert_results_contain(
        check(ttFont), WARN, "too-long", "with a too long description string..."
    )


def test_check_hinting_impact():
    """Show hinting filesize impact."""
    check = CheckTester("com.google.fonts/check/hinting_impact")

    font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_results_contain(
        check(font), INFO, "size-impact", "this check always emits an INFO result..."
    )

    font = TEST_FILE("rokkitt/Rokkitt-Bold.otf")
    assert_results_contain(
        check(font), INFO, "size-impact", "this check always emits an INFO result..."
    )


def test_check_file_size():
    """Ensure files are not too large."""
    # This needs a profile to inject configuration data
    check = CheckTester("com.google.fonts/check/file_size", profile=googlefonts_profile)

    assert_PASS(check(TEST_FILE("mada/Mada-Regular.ttf")))

    assert_results_contain(
        check(TEST_FILE("varfont/inter/Inter[slnt,wght].ttf")),
        WARN,
        "large-font",
        "with quite a big font...",
    )

    assert_results_contain(
        check(TEST_FILE("cjk/SourceHanSans-Regular.otf")),
        FAIL,
        "massive-font",
        "with a very big font...",
    )


def test_check_name_version_format():
    """Version format is correct in 'name' table ?"""
    check = CheckTester("com.google.fonts/check/name/version_format")

    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # then we introduce bad strings in all version-string entries:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.VERSION_STRING:
            invalid = "invalid-version-string".encode(name.getEncoding())
            ttFont["name"].names[i].string = invalid
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-version-strings",
        "with bad version format in name table...",
    )

    # and finally we remove all version-string entries:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.VERSION_STRING:
            del ttFont["name"].names[i]
    assert_results_contain(
        check(ttFont),
        FAIL,
        "no-version-string",
        "with font lacking version string entries in name table...",
    )


def NOT_IMPLEMENTED_test_check_old_ttfautohint():
    """Font has old ttfautohint applied?"""
    # check = CheckTester( "com.google.fonts/check/old_ttfautohint")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, code="lacks-version-strings"
    # - INFO, code="version-not-detected"  "Could not detect which version of
    #                                       ttfautohint was used in this font."
    # - WARN, code="old-ttfa"  "detected an old ttfa version"
    # - PASS
    # - FAIL, code="parse-error"


@pytest.mark.parametrize(
    "expected_status,expected_keyword,reason,font",
    [
        (
            FAIL,
            "lacks-ttfa-params",
            "with a font lacking ttfautohint params on its version strings "
            "on the name table.",
            TEST_FILE("coveredbyyourgrace/CoveredByYourGrace.ttf"),
        ),
        (
            SKIP,
            "not-hinted",
            "with a font which appears to our heuristic as not hinted using "
            "ttfautohint.",
            TEST_FILE("mada/Mada-Regular.ttf"),
        ),
        (
            PASS,
            "ok",
            "with a font that has ttfautohint params"
            ' (-l 6 -r 36 -G 0 -x 10 -H 350 -D latn -f cyrl -w "" -X "")',
            TEST_FILE("merriweather/Merriweather-Regular.ttf"),
        ),
    ],
)
def test_check_has_ttfautohint_params(expected_status, expected_keyword, reason, font):
    """Font has ttfautohint params?"""
    check = CheckTester("com.google.fonts/check/has_ttfautohint_params")

    assert_results_contain(check(font), expected_status, expected_keyword, reason)


def test_check_epar():
    """EPAR table present in font?"""
    check = CheckTester("com.google.fonts/check/epar")

    # Our reference Mada Regular lacks an EPAR table:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must emit an INFO message inviting the designers
    # to learn more about it:
    assert_results_contain(
        check(ttFont), INFO, "lacks-EPAR", "with a font lacking an EPAR table..."
    )

    # add a fake EPAR table to validate the PASS code-path:
    ttFont["EPAR"] = "foo"
    assert_PASS(check(ttFont), "with a good font...")


def NOT_IMPLEMENTED_test_check_gasp():
    """Is GASP table correctly set?"""
    # check = CheckTester( "com.google.fonts/check/gasp")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "lacks-gasp"        "Font is missing the gasp table."
    # - FAIL, "empty"             "The gasp table has no values."
    # - FAIL, "lacks-ffff-range"  "The gasp table does not have a 0xFFFF gasp range."
    # - INFO, "ranges"            "These are the ppm ranges declared on the gasp table:"
    # - WARN, "non-ffff-range"    "The gasp table has a range that may be unneccessary."
    # - WARN, "unset-flags"       "All flags in gasp range 0xFFFF (i.e. all font sizes)
    #                              must be set to 1"
    # - PASS                      "The gasp table is correctly set."


def test_check_name_familyname_first_char():
    """Make sure family name does not begin with a digit."""
    check = CheckTester("com.google.fonts/check/name/familyname_first_char")

    # Our reference Mada Regular is known to be good
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # alter the family-name prepending a digit:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            ttFont["name"].names[i].string = "1badname".encode(name.getEncoding())

    # and make sure the check FAILs:
    assert_results_contain(
        check(ttFont),
        FAIL,
        "begins-with-digit",
        "with a font in which the family name begins with a digit...",
    )


def test_check_name_ascii_only_entries():
    """Are there non-ASCII characters in ASCII-only NAME table entries?"""
    check = CheckTester("com.google.fonts/check/name/ascii_only_entries")

    # Our reference Merriweather Regular is known to be good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    #  The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).
    #  For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that
    #  string should be the same in CFF fonts which also have this
    #  requirement in the OpenType spec.

    # Let's check detection of both. First nameId 6:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.POSTSCRIPT_NAME:
            ttFont["name"].names[i].string = "Infração".encode(encoding="utf-8")

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-string",
        "with non-ascii on nameID 6 entry (Postscript name)...",
    )

    assert_results_contain(
        check(ttFont),
        FAIL,
        "non-ascii-strings",
        "with non-ascii on nameID 6 entry (Postscript name)...",
    )

    # Then reload the good font
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # And check detection of a problem on nameId 0:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont["name"].names[i].string = "Infração".encode(encoding="utf-8")

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-string",
        "with non-ascii on nameID 0 entry (Copyright notice)...",
    )

    assert_results_contain(
        check(ttFont),
        FAIL,
        "non-ascii-strings",
        "with non-ascii on nameID 0 entry (Copyright notice)...",
    )

    # Reload the good font once more:
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    #  Note:
    #  A common place where we find non-ASCII strings is on name table
    #  entries with NameID > 18, which are expressly for localising
    #  the ASCII-only IDs into Hindi / Arabic / etc.

    # Let's check a good case of a non-ascii on the name table then!
    # Choose an arbitrary name entry to mess up with:
    index = 5

    ttFont["name"].names[index].nameID = 19
    ttFont["name"].names[index].string = "Fantástico!".encode(encoding="utf-8")
    assert_PASS(check(ttFont), "with non-ascii on entries with nameId > 18...")


def test_check_metadata_unique_full_name_values():
    """METADATA.pb: check if fonts field only has unique "full_name" values."""
    check = CheckTester("com.google.fonts/check/metadata/unique_full_name_values")

    # Our reference FamilySans family is good:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font), "with a good family...")

    # then duplicate a full_name entry to make it FAIL:
    md = Font(font).family_metadata
    md.fonts[0].full_name = md.fonts[1].full_name
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "duplicated",
        "with a duplicated full_name entry.",
    )


def test_check_metadata_unique_weight_style_pairs():
    """METADATA.pb: check if fonts field only contains unique style:weight pairs."""
    check = CheckTester("com.google.fonts/check/metadata/unique_weight_style_pairs")

    # Our reference FamilySans family is good:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font), "with a good family...")

    # then duplicate a pair of style & weight entries to make it FAIL:
    md = Font(font).family_metadata
    md.fonts[0].style = md.fonts[1].style
    md.fonts[0].weight = md.fonts[1].weight
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "duplicated",
        "with a duplicated pair of style & weight entries",
    )


def test_check_metadata_license():
    """METADATA.pb license is "APACHE2", "UFL" or "OFL"?"""
    check = CheckTester("com.google.fonts/check/metadata/license")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    good_licenses = ["APACHE2", "UFL", "OFL"]
    some_bad_values = ["APACHE", "Apache", "Ufl", "Ofl", "Open Font License"]

    check(font)
    md = Font(font).family_metadata
    for good in good_licenses:
        md.license = good
        assert_PASS(check(MockFont(file=font, family_metadata=md)), f": {good}")

    for bad in some_bad_values:
        md.license = bad
        assert_results_contain(
            check(MockFont(file=font, family_metadata=md)),
            FAIL,
            "bad-license",
            f": {bad}",
        )


def test_check_metadata_menu_and_latin():
    """METADATA.pb should contain at least "menu" and "latin" subsets."""
    check = CheckTester("com.google.fonts/check/metadata/menu_and_latin")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    good_cases = [
        ["menu", "latin"],
        ["menu", "cyrillic", "latin"],
    ]

    bad_cases = [["menu"], ["latin"], [""], ["latin", "cyrillyc"], ["khmer"]]

    md = Font(font).family_metadata
    for good in good_cases:
        del md.subsets[:]
        md.subsets.extend(good)
        assert_PASS(
            check(MockFont(file=font, family_metadata=md)), f"with subsets = {good}"
        )

    for bad in bad_cases:
        del md.subsets[:]
        md.subsets.extend(bad)
        assert_results_contain(
            check(MockFont(file=font, family_metadata=md)),
            FAIL,
            "missing",
            f"with subsets = {bad}",
        )


def test_check_metadata_subsets_order():
    """METADATA.pb subsets should be alphabetically ordered."""
    check = CheckTester("com.google.fonts/check/metadata/subsets_order")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

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

    md = Font(font).family_metadata
    for good in good_cases:
        del md.subsets[:]
        md.subsets.extend(good)
        assert_PASS(
            check(MockFont(file=font, family_metadata=md)), f"with subsets = {good}"
        )

    md = Font(font).family_metadata
    for bad in bad_cases:
        del md.subsets[:]
        md.subsets.extend(bad)
        assert_results_contain(
            check(MockFont(file=font, family_metadata=md)),
            FAIL,
            "not-sorted",
            f"with subsets = {bad}",
        )


def test_check_metadata_includes_production_subsets():
    """Check METADATA.pb has production subsets."""
    check = CheckTester(
        "com.google.fonts/check/metadata/includes_production_subsets",
    )

    # We need to use a family that is already in production
    # Our reference Cabin is known to be good
    fonts = cabin_fonts

    # So it must PASS the check:
    assert_PASS(check(fonts), "with a good METADATA.pb for this family...")

    # Then we induce the problem by removing a subset:
    md = Font(fonts[0]).family_metadata
    md.subsets.pop()
    assert_results_contain(
        check(MockFont(file=fonts[0], family_metadata=md)),
        FAIL,
        "missing-subsets",
        "with a bad METADATA.pb (last subset has been removed)...",
    )


def test_check_metadata_copyright():
    """METADATA.pb: Copyright notice is the same in all fonts?"""
    check = CheckTester("com.google.fonts/check/metadata/copyright")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know its copyright notices are consistent:
    assert_PASS(check(font), "with consistent copyright notices on FamilySans...")

    # Now we make them diverge:
    md = Font(font).family_metadata
    md.fonts[1].copyright = (
        md.fonts[0].copyright + " arbitrary suffix!"
    )  # to make it different

    # To ensure the problem is detected:
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "inconsistency",
        "with diverging copyright notice strings...",
    )


def test_check_metadata_familyname():
    """Check that METADATA.pb family values are all the same."""
    check = CheckTester("com.google.fonts/check/metadata/familyname")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know its family name entries on METADATA.pb are consistent:
    assert_PASS(check(font), "with consistent family name...")

    # Now we make them diverge:
    md = Font(font).family_metadata
    md.fonts[1].name = md.fonts[0].name + " arbitrary suffix!"  # to make it different

    # To ensure the problem is detected:
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "inconsistency",
        "With diverging Family name metadata entries...",
    )


def test_check_metadata_has_regular():
    """
    METADATA.pb: According Google Fonts standards, families should have a Regular style.
    """
    check = CheckTester("com.google.fonts/check/metadata/has_regular")

    # Let's start with our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans has got a regular declares in its METADATA.pb file:
    assert_PASS(check(font), "with Family Sans, a family with a regular style...")

    # We remove the regular:
    md = Font(font).family_metadata
    for i in range(len(md.fonts)):
        if md.fonts[i].filename == "FamilySans-Regular.ttf":
            del md.fonts[i]
            break

    # and make sure the check now FAILs:
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "lacks-regular",
        "with a METADATA.pb file without a regular...",
    )


def test_check_metadata_regular_is_400():
    """METADATA.pb: Regular should be 400."""
    check = CheckTester("com.google.fonts/check/metadata/regular_is_400")

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans' Regular has a weight value equal to 400,
    # so the check should PASS:
    assert_PASS(check(font), "with Family Sans, a family with regular=400...")

    md = Font(font).family_metadata
    # Then we swap the values of the Regular and Medium:
    for i in range(len(md.fonts)):
        if md.fonts[i].filename == "FamilySans-Regular.ttf":
            md.fonts[i].weight = 500
        if md.fonts[i].filename == "FamilySans-Medium.ttf":
            md.fonts[i].weight = 400

    # and make sure the check now FAILs:
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "not-400",
        "with METADATA.pb with regular=500...",
    )

    # Now we change the value of the Medium back to 500. The check will be skipped
    # because the family now has no Regular style.
    for i in range(len(md.fonts)):
        if md.fonts[i].filename == "FamilySans-Medium.ttf":
            md.fonts[i].weight = 500
    msg = assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), SKIP, "unfulfilled-conditions"
    )
    assert "Unfulfilled Conditions: has_regular_style" in msg


def test_check_metadata_nameid_post_script_name():
    """Checks METADATA.pb font.post_script_name matches
    postscript name declared on the name table."""
    check = CheckTester("com.google.fonts/check/metadata/nameid/post_script_name")

    # Let's start with the METADATA.pb file from our reference FamilySans family:
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")

    # We know that Family Sans Regular is good here:
    assert_PASS(check(font))

    # Then cause it to fail:
    md = Font(font).font_metadata
    md.post_script_name = "Foo"
    assert_results_contain(
        check(MockFont(file=font, font_metadata=md)), FAIL, "mismatch"
    )

    # TODO: the failure-mode below seems more generic than the scope
    #       of this individual check. This could become a check by itself!
    #
    # code-paths:
    # - FAIL code="missing", "Font lacks a POSTSCRIPT_NAME"


def test_check_metadata_nameid_font_name():
    """
    METADATA.pb font.name value should be same as the family name declared on
    the name table.
    """
    check = CheckTester("com.google.fonts/check/metadata/nameid/font_name")

    # Our reference Merriweather-Regular is know to have good fullname metadata
    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    ttFont = TTFont(font)
    assert_PASS(check(ttFont), "with a good font...")

    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            good = name.string.decode(
                name.getEncoding()
            )  # keep a copy of the good value
            ttFont["name"].names[i].string = (good + "bad-suffix").encode(
                name.getEncoding()
            )
            assert_results_contain(
                check(ttFont),
                FAIL,
                "mismatch",
                f"with a bad FULL_FONT_NAME entry ({i})...",
            )
            ttFont["name"].names[i].string = good  # restore good value

    # We also want to make sure that name id 16, whenever present,
    # is used to compute the expected familyname.
    # Tiro Devanagari Hindi is a good exampmle of this:
    font = TEST_FILE("tirodevanagarihindi/TiroDevanagariHindi-Regular.ttf")
    assert_PASS(check(font), "with a good font containing name id 16...")

    # Good font with other language name entries
    font = TEST_FILE("bizudpmincho-nameonly/BIZUDPMincho-Regular.ttf")

    assert_PASS(check(font), "with a good font with other languages...")

    # TODO:
    # FAIL, "lacks-entry"


def test_check_metadata_match_fullname_postscript():
    """METADATA.pb family.full_name and family.post_script_name
    fields have equivalent values ?"""
    check = CheckTester("com.google.fonts/check/metadata/match_fullname_postscript")

    regular_font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    lightitalic_font = TEST_FILE("merriweather/Merriweather-LightItalic.ttf")

    assert_PASS(
        check(lightitalic_font), "with good entries (Merriweather-LightItalic)..."
    )
    #            post_script_name: "Merriweather-LightItalic"
    #            full_name:        "Merriweather Light Italic"

    # TODO: Verify why/whether "Regular" cannot be omited on font.full_name
    #       There's some relevant info at:
    #       https://github.com/fonttools/fontbakery/issues/1517
    #
    # FIXME: com.google.fonts/check/metadata/nameid/family_and_full_names
    #        ties the full_name values from the METADATA.pb file and the
    #        internal name table entry (FULL_FONT_NAME)
    #        to be strictly identical. So it seems that the test below is
    #        actually wrong (as well as the current implementation):
    #
    assert_results_contain(
        check(regular_font),
        FAIL,
        "mismatch",
        "with bad entries (Merriweather-Regular)...",
    )
    #                       post_script_name: "Merriweather-Regular"
    #                       full_name:        "Merriweather"

    # fix the regular metadata:
    md = Font(regular_font).font_metadata
    md.full_name = "Merriweather Regular"

    assert_PASS(
        check(MockFont(file=regular_font, font_metadata=md)),
        "with good entries (Merriweather-Regular after full_name fix)...",
    )
    #            post_script_name: "Merriweather-Regular"
    #            full_name:        "Merriweather Regular"

    # introduce an error in the metadata:
    md.full_name = "MistakenFont Regular"

    assert_results_contain(
        check(MockFont(file=regular_font, font_metadata=md)),
        FAIL,
        "mismatch",
        "with a mismatch...",
    )
    #                       post_script_name: "Merriweather-Regular"
    #                       full_name:        "MistakenFont Regular"


def NOT_IMPLEMENTED_test_check_match_filename_postscript():
    """METADATA.pb family.filename and family.post_script_name
    fields have equivalent values?"""
    # check = CheckTester( "com.google.fonts/check/match_filename_postscript")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "mismatch"		"METADATA.pb filename does not match post_script_name"
    # - PASS


MONTSERRAT_RIBBI = [
    TEST_FILE("montserrat/Montserrat-Regular.ttf"),
    TEST_FILE("montserrat/Montserrat-Italic.ttf"),
    TEST_FILE("montserrat/Montserrat-Bold.ttf"),
    TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
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
    TEST_FILE("montserrat/Montserrat-Thin.ttf"),
]


def test_check_metadata_valid_full_name_values():
    """METADATA.pb font.full_name field contains font name in right format?"""
    check = CheckTester("com.google.fonts/check/metadata/valid_full_name_values")

    # Our reference Montserrat family is a good 18-styles family:
    # properly described in its METADATA.pb file:
    for font in MONTSERRAT_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(font), "with a good RIBBI font ({fontfile})...")

        # And fail if the full familyname in METADATA.pb diverges
        # from the name inferred from the name table:
        assert_results_contain(
            check(MockFont(file=font, font_familynames=["WrongFamilyName"])),
            FAIL,
            "mismatch",
            f"with a bad RIBBI font ({font})...",
        )

    # We do the same for NON-RIBBI styles:
    for font in MONTSERRAT_NON_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(font), f"with a good NON-RIBBI font ({font})...")

        # Unless when not matching typographic familyname from the name table:
        assert_results_contain(
            check(MockFont(file=font, typographic_familynames=["WrongFamilyName"])),
            FAIL,
            "mismatch",
            f"with a bad NON-RIBBI font ({font})...",
        )

    # Good font with other language name entries
    font = TEST_FILE("bizudpmincho-nameonly/BIZUDPMincho-Regular.ttf")

    assert_PASS(check(font), "with a good font with other languages...")


def test_check_metadata_valid_filename_values():
    """METADATA.pb font.filename field contains font name in right format?"""
    check = CheckTester("com.google.fonts/check/metadata/valid_filename_values")

    # Our reference Montserrat family is a good 18-styles family:
    for font in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(font), f"with a good font ({font})...")

        # And fail if it finds a bad filename:
        meta = Font(font).family_metadata
        for i in range(len(meta.fonts)):
            meta.fonts[i].filename = "WrongFileName"
        assert_results_contain(
            check(MockFont(file=font, family_metadata=meta)),
            FAIL,
            "bad-field",
            f'with bad filename metadata ("WrongFileName")'
            f' for fontfile "{font}"...',
        )


def test_check_metadata_valid_post_script_name_values():
    """METADATA.pb font.post_script_name field contains font name in right format?"""
    check = CheckTester(
        "com.google.fonts/check/metadata/valid_post_script_name_values",
    )

    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        # So it must PASS the check:
        assert_PASS(check(fontfile), f"with a good font ({fontfile})...")

        # And fail if it finds a bad filename:
        md = Font(fontfile).font_metadata
        md.post_script_name = "WrongPSName"
        assert_results_contain(
            check(MockFont(file=fontfile, font_metadata=md)),
            FAIL,
            "mismatch",
            f"with a bad font ({fontfile})...",
        )

    # Good font with other language name entries
    font = TEST_FILE("bizudpmincho-nameonly/BIZUDPMincho-Regular.ttf")

    assert_PASS(check(font), "with a good font with other languages...")


def test_check_metadata_valid_nameid25():
    """Check name ID 25 to end with "Italic" for Italic VFs"""
    check = CheckTester("com.google.fonts/check/metadata/valid_nameid25")

    # PASS
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont), f"with a good font ({ttFont})...")
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont), f"with a good font ({ttFont})...")

    def set_name(font, nameID, string):
        for record in font["name"].names:
            if record.nameID == nameID:
                old_string = record.toUnicode()
                if string != old_string:
                    font["name"].setName(
                        string,
                        record.nameID,
                        record.platformID,
                        record.platEncID,
                        record.langID,
                    )

    # FAIL
    fontpath = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(fontpath)
    set_name(ttFont, 25, "ShantellSans")
    assert_results_contain(
        check(MockFont(file=fontpath, ttFont=ttFont)),
        FAIL,
        "nameid25-missing-italic",
        f"with a bad font ({ttFont})...",
    )
    set_name(ttFont, 25, "ShantellSans Italic")
    assert_results_contain(
        check(MockFont(file=fontpath, ttFont=ttFont)),
        FAIL,
        "nameid25-has-spaces",
        f"with a bad font ({ttFont})...",
    )


# note: The copyright checks do not actually verify that the project name is correct.
#       They only focus on the string format.
GOOD_COPYRIGHT_NOTICE_STRINGS = (
    (
        "Copyright 2017 The Archivo Black Project Authors"
        " (https://github.com/Omnibus-Type/ArchivoBlack)"
    ),
    (
        "Copyright 2017-2018 The YearRange Project Authors"
        " (https://github.com/Looks/Good)"
    ),
    (
        "Copyright 2012-2014, 2016, 2019-2021, 2023 The MultiYear Project Authors"
        " (https://github.com/With/ManyRanges)"
    ),
)


def test_check_metadata_valid_copyright():
    """Copyright notice on METADATA.pb matches canonical pattern ?"""
    check = CheckTester("com.google.fonts/check/metadata/valid_copyright")

    # Our reference Cabin Regular is known to be bad
    # Since it provides an email instead of a git URL:
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(
        check(font), FAIL, "bad-notice-format", "with a bad copyright notice string..."
    )

    # Then, to make the check PASS, we change it into a few good strings:
    for good_string in GOOD_COPYRIGHT_NOTICE_STRINGS:
        md = Font(font).font_metadata
        md.copyright = good_string
        assert_PASS(
            check(MockFont(file=font, font_metadata=md)),
            "with a good copyright notice string...",
        )

        # We also ignore case, so these should also PASS:
        md.copyright = good_string.upper()
        assert_PASS(
            check(MockFont(file=font, font_metadata=md)), "with all uppercase..."
        )

        md.copyright = good_string.lower()
        assert_PASS(
            check(MockFont(file=font, font_metadata=md)), "with all lowercase..."
        )


def test_check_font_copyright():
    """Copyright notices match canonical pattern in fonts"""
    check = CheckTester("com.google.fonts/check/font_copyright")

    # Our reference Cabin Regular is known to be bad
    # since it provides an email instead of a git URL:
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-notice-format",
        "with a bad copyright notice string...",
    )

    # Then, to make the check PASS, we change it into a few good strings:
    for good_string in GOOD_COPYRIGHT_NOTICE_STRINGS:
        for i, entry in enumerate(ttFont["name"].names):
            if entry.nameID == NameID.COPYRIGHT_NOTICE:
                ttFont["name"].names[i].string = good_string.encode(entry.getEncoding())
        assert_PASS(check(ttFont), "with good strings...")


def DISABLE_test_check_glyphs_file_font_copyright():
    """Copyright notices match canonical pattern in fonts"""
    check = CheckTester("com.google.fonts/check/glyphs_file/font_copyright")

    glyphsFile = GLYPHSAPP_TEST_FILE("Comfortaa.glyphs")
    # note: the check does not actually verify that the project name is correct.
    #       It only focuses on the string format.

    # Use an email instead of a git URL:
    bad_string = (
        "Copyright 2017 The Archivo Black Project Authors"
        " (contact-us@fake-address.com)"
    )
    glyphsFile.copyright = bad_string
    assert_results_contain(
        check(glyphsFile),
        FAIL,
        "bad-notice-format",
        "with a bad copyright notice string...",
    )

    # We change it into a good string (example extracted from Archivo Black):
    good_string = (
        "Copyright 2017 The Archivo Black Project Authors"
        " (https://github.com/Omnibus-Type/ArchivoBlack)"
    )
    glyphsFile.copyright = good_string
    assert_PASS(check(glyphsFile), "with a good coopyright string...")


def test_check_metadata_reserved_font_name():
    """Copyright notice on METADATA.pb should not contain Reserved Font Name."""
    check = CheckTester("com.google.fonts/check/metadata/reserved_font_name")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good copyright notice string...")

    # Then we make it bad:
    md = Font(font).font_metadata
    md.copyright += "Reserved Font Name"
    assert_results_contain(
        check(MockFont(file=font, font_metadata=md)),
        WARN,
        "rfn",
        'with a notice containing "Reserved Font Name"...',
    )


def test_check_metadata_copyright_max_length():
    """METADATA.pb: Copyright notice shouldn't exceed 500 chars."""
    check = CheckTester("com.google.fonts/check/metadata/copyright_max_length")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    check(font)
    md = Font(font).font_metadata

    md.copyright = 500 * "x"
    assert_PASS(
        check(MockFont(file=font, font_metadata=md)),
        "with a 500-char copyright notice string...",
    )

    md.copyright = 501 * "x"
    assert_results_contain(
        check(MockFont(file=font, font_metadata=md)),
        FAIL,
        "max-length",
        "with a 501-char copyright notice string...",
    )


def test_check_metadata_filenames():
    """METADATA.pb: Font filenames match font.filename entries?"""
    check = CheckTester("com.google.fonts/check/metadata/filenames")

    assert_PASS(check(rosarivo_fonts), "with matching list of font files...")

    # make sure missing files are detected by the check:
    fonts = rosarivo_fonts
    original_name = fonts[0]
    # rename one font file in order to trigger the FAIL
    os.rename(original_name, "font.tmp")
    assert_results_contain(
        check(fonts), FAIL, "file-not-found", "with missing font files..."
    )
    os.rename("font.tmp", original_name)  # restore filename

    # From all TTFs in Cabin's directory, the condensed ones are not
    # listed on METADATA.pb, so the check must FAIL, even if we do not
    # explicitely include them in the set of files to be checked:
    assert_results_contain(
        check(cabin_fonts),
        FAIL,
        "file-not-declared",
        "with some font files not declared...",
    )


def test_check_metadata_nameid_family_and_full_names():
    """
    METADATA.pb font.name and font.full_name fields match the values declared on
    the name table?
    """
    check = CheckTester(
        "com.google.fonts/check/metadata/nameid/family_and_full_names",
    )

    # Our reference Merriweather Regular is known to be good here.
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # There we go again!
    # Breaking FULL_FONT_NAME entries one by one:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FULL_FONT_NAME:
            backup = name.string
            ttFont["name"].names[i].string = "This is utterly wrong!".encode(
                name.getEncoding()
            )
            assert_results_contain(
                check(ttFont),
                FAIL,
                "fullname-mismatch",
                "with a METADATA.pb / FULL_FONT_NAME mismatch...",
            )
            # and restore the good value:
            ttFont["name"].names[i].string = backup

    # And then we do the same with FONT_FAMILY_NAME entries:
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.FONT_FAMILY_NAME:
            backup = name.string
            ttFont["name"].names[i].string = (
                "I'm listening to" " The Players with Hiromasa Suzuki - Galaxy (1979)"
            ).encode(name.getEncoding())
            assert_results_contain(
                check(ttFont),
                FAIL,
                "familyname-mismatch",
                "with a METADATA.pb / FONT_FAMILY_NAME mismatch...",
            )
            # and restore the good value:
            ttFont["name"].names[i].string = backup


def test_check_metadata_match_name_familyname():
    """METADATA.pb: Check font name is the same as family name."""
    check = CheckTester("com.google.fonts/check/metadata/match_name_familyname")

    # Our reference Cabin Regular is known to be good
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good font...")

    # Then we FAIL with mismatching names:
    family_md = Font(font).family_metadata
    font_md = Font(font).font_metadata
    family_md.name = "Some Fontname"
    font_md.name = "Something Else"
    assert_results_contain(
        check(MockFont(file=font, family_metadata=family_md, font_metadata=font_md)),
        FAIL,
        "mismatch",
        "with bad font/family name metadata...",
    )


def test_check_check_metadata_canonical_weight_value():
    """METADATA.pb: Check that font weight has a canonical value."""
    check = CheckTester("com.google.fonts/check/metadata/canonical_weight_value")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    check(font)
    md = Font(font).font_metadata

    for w in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
        md.weight = w
        assert_PASS(
            check(MockFont(file=font, font_metadata=md)),
            f"with a good weight value ({w})...",
        )

    for w in [150, 250, 350, 450, 550, 650, 750, 850]:
        md.weight = w
        assert_results_contain(
            check(MockFont(file=font, font_metadata=md)),
            FAIL,
            "bad-weight",
            "with a bad weight value ({w})...",
        )


def test_check_metadata_os2_weightclass():
    """Checking OS/2 usWeightClass matches weight specified at METADATA.pb"""
    check = CheckTester("com.google.fonts/check/metadata/os2_weightclass")

    # === test cases for Variable Fonts ===
    # Our reference Jura is known to be good
    font = TEST_FILE("varfont/jura/Jura[wght].ttf")
    assert_PASS(check(font), "with a good metadata...")

    # Should report if a bad weight value is ifound though:
    md = Font(font).font_metadata
    good_value = md.weight
    bad_value = good_value + 100
    md.weight = bad_value
    assert_results_contain(
        check(MockFont(file=font, font_metadata=md)),
        FAIL,
        "mismatch",
        "with a bad metadata...",
    )

    font = TEST_FILE("leaguegothic-vf/LeagueGothic[wdth].ttf")
    assert_PASS(check(font), 'with a good VF that lacks a "wght" axis....')
    # See: https://github.com/fonttools/fontbakery/issues/3529

    # === test cases for Static Fonts ===
    # Our reference Montserrat family is a good 18-styles family:
    for fontfile in MONTSERRAT_RIBBI + MONTSERRAT_NON_RIBBI:
        ttFont = TTFont(fontfile)
        assert_PASS(check(ttFont), f"with a good font ({fontfile})...")

        # but should report bad weight values:
        md = Font(font).font_metadata
        good_value = md.weight
        bad_value = good_value + 50
        md.weight = bad_value
        assert_results_contain(
            check(MockFont(file=font, font_metadata=md)),
            FAIL,
            "mismatch",
            f"with bad metadata for {fontfile}...",
        )

        # If font is Thin or ExtraLight, ensure that this check can
        # accept both 100, 250 for Thin and 200, 275 for ExtraLight
        if "Thin" in fontfile:
            ttFont["OS/2"].usWeightClass = 100
            assert_PASS(check(ttFont), f"with weightclass 100 on ({fontfile})...")

            ttFont["OS/2"].usWeightClass = 250
            assert_PASS(check(ttFont), f"with weightclass 250 on ({fontfile})...")

        if "ExtraLight" in fontfile:
            ttFont["OS/2"].usWeightClass = 200
            assert_PASS(check(ttFont), f"with weightClass 200 on ({fontfile})...")

            ttFont["OS/2"].usWeightClass = 275
            assert_PASS(check(ttFont), f"with weightClass 275 on ({fontfile})...")


def NOT_IMPLEMENTED_test_check_metadata_match_weight_postscript():
    """METADATA.pb: Metadata weight matches postScriptName."""
    # check = CheckTester( "com.google.fonts/check/metadata/match_weight_postscript")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "METADATA.pb: Font weight value is invalid."
    # - FAIL, "METADATA.pb: Mismatch between postScriptName and weight value."
    # - PASS


def NOT_IMPLEMENTED_test_check_metadata_canonical_style_names():
    """METADATA.pb: Font styles are named canonically?"""
    # check = CheckTester( "com.google.fonts/check/metadata/canonical_style_names")
    # TODO: Implement-me!
    #
    # code-paths:
    # - SKIP		    "Applicable only to font styles declared as 'italic' or 'normal'
    #                    on METADATA.pb."
    # - FAIL, "italic"	"Font style should be italic."
    # - FAIL, "normal"	"Font style should be normal."
    # - PASS		    "Font styles are named canonically."


def test_check_metadata_consistent_repo_urls():
    """
    METADATA.pb: Check URL on copyright string is the same as in repository_url field.
    """
    check = CheckTester("com.google.fonts/check/metadata/consistent_repo_urls")

    # The problem was first seen on a project with these diverging values:
    # copyright: "Copyright 2022 The Delicious Handrawn Project Authors
    #             (https://github.com/duartp/gloock)"
    # repository_url: "https://github.com/alphArtype/Delicious-Handrawn"
    font = TEST_FILE("delicioushandrawn/DeliciousHandrawn-Regular.ttf")
    assert_results_contain(check(font), FAIL, "mismatch", "with different URLs...")

    family_md = Font(font).family_metadata
    # so we fix it:
    assert (
        family_md.source.repository_url
        == "https://github.com/alphArtype/Delicious-Handrawn"
    )
    family_md.fonts[0].copyright = (
        "Copyright 2022 The Delicious Handrawn Project Authors"
        " (https://github.com/alphArtype/Delicious-Handrawn)"
    )
    assert_PASS(check(MockFont(file=font, family_metadata=family_md)))

    family_md.source.repository_url = ""
    assert_results_contain(
        check(MockFont(file=font, family_metadata=family_md)),
        FAIL,
        "lacks-repo-url",
        "when the field is either empty or completley missing...",
    )

    # League Gothic got a bad repo in DESCRIPTION.en.html
    ttFont = TTFont(TEST_FILE("leaguegothic-vf/LeagueGothic[wdth].ttf"))
    assert_results_contain(check(ttFont), FAIL, "mismatch", "with different URLs...")

    # CabinVF got a bad repo in OFL.txt
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_results_contain(check(ttFont), FAIL, "mismatch", "with different URLs...")


def test_check_metadata_primary_script():
    """METADATA.pb: Check for primary_script"""
    check = CheckTester("com.google.fonts/check/metadata/primary_script")

    class Metadata:
        primary_script = ""

    family_md = Metadata()
    font = TEST_FILE("fira/FiraCode[wght].ttf")
    family_md.primary_script = ""
    assert_results_contain(
        check(MockFont(file=font, family_metadata=family_md)),
        WARN,
        "missing-primary-script",
    )
    family_md.primary_script = "Arab"
    assert_results_contain(
        check(MockFont(file=font, family_metadata=family_md)),
        WARN,
        "wrong-primary-script",
    )
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont))


def test_check_unitsperem_strict():
    """Stricter unitsPerEm criteria for Google Fonts."""
    check = CheckTester("com.google.fonts/check/unitsperem_strict")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    PASS_VALUES = [
        16,
        32,
        64,
        128,
        256,
        512,
        1024,
    ]  # Good for better performance on legacy renderers
    PASS_VALUES.extend([500, 1000])  # or common typical values
    PASS_VALUES.extend([2000, 2048])  # not so common, but still ok

    FAIL_LARGE_VALUES = [4096, 16385]  # uncommon and large,
    # and finally the bad ones, including:
    FAIL_BAD_VALUES = [0, 1, 2, 4, 8, 15]  # simply invalid

    for pass_value in PASS_VALUES:
        ttFont["head"].unitsPerEm = pass_value
        assert_PASS(check(ttFont), f"with unitsPerEm = {pass_value}...")

    for warn_value in FAIL_LARGE_VALUES:
        ttFont["head"].unitsPerEm = warn_value
        assert_results_contain(
            check(ttFont), FAIL, "large-value", f"with unitsPerEm = {warn_value}..."
        )

    for fail_value in FAIL_BAD_VALUES:
        ttFont["head"].unitsPerEm = fail_value
        assert_results_contain(
            check(ttFont), FAIL, "bad-value", f"with unitsPerEm = {fail_value}..."
        )


def NOT_IMPLEMENTED_test_check_version_bump():
    """Version number has increased since previous release on Google Fonts?"""
    # check = CheckTester( "com.google.fonts/check/version_bump")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "Version number is equal to version on Google Fonts."
    # - FAIL, "Version number is less than version on Google Fonts."
    # - FAIL, "Version number is equal to version on Google Fonts GitHub repo."
    # - FAIL, "Version number is less than version on Google Fonts GitHub repo."
    # - PASS


def NOT_IMPLEMENTED_test_check_production_glyphs_similarity():
    """Glyphs are similiar to Google Fonts version?"""
    # check = CheckTester( "com.google.fonts/check/production_glyphs_similarity")
    # TODO: Implement-me!
    #
    # code-paths:
    # - WARN, "Following glyphs differ greatly from Google Fonts version"
    # - PASS, "Glyphs are similar"


def test_check_italic_angle():
    """Checking post.italicAngle value."""
    check = CheckTester(
        "com.google.fonts/check/italic_angle",
        profile=googlefonts_profile,
    )

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    ttFont = TTFont(font)

    # italic-angle, style, fail_message
    test_cases = [
        [1, "Italic", FAIL, "positive"],
        [0, "Regular", PASS, None],  # This must PASS as it is a non-italic
        [-21, "ThinItalic", WARN, "over-20-degrees"],
        [-30, "ThinItalic", WARN, "over-20-degrees"],
        [-31, "ThinItalic", FAIL, "over-30-degrees"],
        [-91, "ThinItalic", FAIL, "over-90-degrees"],
        [0, "Italic", FAIL, "zero-italic"],
        [-1, "ExtraBold", FAIL, "non-zero-upright"],
    ]

    for value, style, expected_result, expected_msg in test_cases:
        ttFont["post"].italicAngle = value

        if expected_result != PASS:
            assert_results_contain(
                check(MockFont(file=font, ttFont=ttFont, style=style)),
                expected_result,
                expected_msg,
                f"with italic-angle:{value} style:{style}...",
            )
        else:
            assert_PASS(
                check(MockFont(file=font, ttFont=ttFont, style=style)),
                f"with italic-angle:{value} style:{style}...",
            )

    # Cairo, check left and right-leaning explicitly
    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.rightslanted.ttf"))
    assert_PASS(check(MockFont(file=font, ttFont=ttFont, style="Italic")))
    ttFont["post"].italicAngle *= -1
    assert_results_contain(
        check(MockFont(file=font, ttFont=ttFont, style="Italic")), FAIL, "positive"
    )

    ttFont = TTFont(TEST_FILE("cairo/CairoPlay-Italic.leftslanted.ttf"))
    assert_PASS(check(MockFont(file=font, ttFont=ttFont, style="Italic")))
    ttFont["post"].italicAngle *= -1
    assert_results_contain(
        check(MockFont(file=font, ttFont=ttFont, style="Italic")), FAIL, "negative"
    )


def test_check_slant_direction():
    """Checking direction of slnt axis angles"""
    check = CheckTester("com.google.fonts/check/slant_direction")

    font = TEST_FILE("slant_direction/Cairo_correct_slnt_axis.ttf")
    assert_PASS(check(font))

    font = TEST_FILE("slant_direction/Cairo_wrong_slnt_axis.ttf")
    assert_results_contain(check(font), FAIL, "positive-value-for-clockwise-lean")


# FIXME!
# GFonts hosted Cabin files seem to have changed in ways
# that break some of the assumptions in the code-test below.
# More info at https://github.com/fonttools/fontbakery/issues/2581
@pytest.mark.xfail(strict=True)
def test_check_production_encoded_glyphs(cabin_ttFonts):
    """Check glyphs are not missing when compared to version on fonts.google.com"""
    check = CheckTester("com.google.fonts/check/production_encoded_glyphs")

    for font in cabin_fonts:
        # Cabin font hosted on fonts.google.com contains
        # all the glyphs for the font in data/test/cabin
        assert_PASS(check(font), f"with '{font}'")

        ttFont = TTFont(font)
        # Take A glyph out of font
        ttFont["cmap"].getcmap(3, 1).cmap.pop(ord("A"))
        ttFont["glyf"].glyphs.pop("A")
        assert_results_contain(check(ttFont), FAIL, "lost-glyphs")


def test_check_metadata_nameid_copyright():
    """Copyright field for this font on METADATA.pb matches
    all copyright notice entries on the name table?"""
    check = CheckTester("com.google.fonts/check/metadata/nameid/copyright")
    from fontbakery.utils import get_name_entry_strings

    # Our reference Cabin Regular is known to be good
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a good METADATA.pb for this font...")

    # But the check must report when mismatching names are found:
    good_value = get_name_entry_strings(Font(font).ttFont, NameID.COPYRIGHT_NOTICE)[0]
    md = Font(font).font_metadata
    md.copyright = good_value + "something bad"
    assert_results_contain(
        check(MockFont(file=font, font_metadata=md)),
        FAIL,
        "mismatch",
        "with a bad METADATA.pb (with a copyright string not matching this font)...",
    )


def test_check_metadata_category():
    """Category field for this font on METADATA.pb is valid?"""
    check = CheckTester("com.google.fonts/check/metadata/category")

    # Our reference Cabin family...
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    check(font)
    md = Font(font).family_metadata
    assert md.category == ["SANS_SERIF"]  # ...is known to be good ;-)
    assert_PASS(check(font), "with a good METADATA.pb...")

    # We then report a problem with this sample of bad values:
    for bad_value in ["SAN_SERIF", "MONO_SPACE", "sans_serif", "monospace"]:
        md.category[:] = [bad_value]
        assert_results_contain(
            check(MockFont(file=font, family_metadata=md)),
            FAIL,
            "bad-value",
            f'with a bad category "{bad_value}"...',
        )

    # And we accept the good ones:
    for good_value in ["MONOSPACE", "SANS_SERIF", "SERIF", "DISPLAY", "HANDWRITING"]:
        md.category[:] = [good_value]
        assert_PASS(
            check(MockFont(file=font, family_metadata=md)), f'with "{good_value}"...'
        )


@pytest.mark.parametrize(
    """fp,mod,result""",
    [
        # tests from test_check_name_familyname:
        (TEST_FILE("cabin/Cabin-Regular.ttf"), {}, PASS),
        (
            TEST_FILE("cabin/Cabin-Regular.ttf"),
            {NameID.FONT_FAMILY_NAME: "Wrong"},
            FAIL,
        ),
        (TEST_FILE("overpassmono/OverpassMono-Regular.ttf"), {}, PASS),
        (TEST_FILE("overpassmono/OverpassMono-Bold.ttf"), {}, PASS),
        (TEST_FILE("overpassmono/OverpassMono-Regular.ttf"), {1: "Foo"}, FAIL),
        (TEST_FILE("merriweather/Merriweather-Black.ttf"), {}, PASS),
        (TEST_FILE("merriweather/Merriweather-LightItalic.ttf"), {}, PASS),
        (
            TEST_FILE("merriweather/Merriweather-LightItalic.ttf"),
            {NameID.FONT_FAMILY_NAME: "Merriweather Light Italic"},
            FAIL,
        ),
        (TEST_FILE("abeezee/ABeeZee-Regular.ttf"), {}, PASS),
        # tests from test_check_name_subfamilyname
        (TEST_FILE("overpassmono/OverpassMono-Regular.ttf"), {}, PASS),
        (TEST_FILE("overpassmono/OverpassMono-Bold.ttf"), {}, PASS),
        (TEST_FILE("merriweather/Merriweather-Black.ttf"), {}, PASS),
        (TEST_FILE("merriweather/Merriweather-LightItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-BlackItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Black.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Bold.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraBoldItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraBold.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraLightItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Italic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-LightItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Light.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-MediumItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Medium.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Regular.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-SemiBoldItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-SemiBold.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"), {}, PASS),
        (TEST_FILE("montserrat/Montserrat-Thin.ttf"), {}, PASS),
        (
            TEST_FILE("montserrat/Montserrat-ThinItalic.ttf"),
            {NameID.FONT_SUBFAMILY_NAME: "Not a proper style"},
            FAIL,
        ),
        # tests from test_check_name_fullfontname
        (TEST_FILE("cabin/Cabin-Regular.ttf"), {}, PASS),
        # warn should be raised since full name is missing Regular
        (TEST_FILE("cabin/Cabin-Regular.ttf"), {4: "Cabin"}, WARN),
        (TEST_FILE("cabin/Cabin-BoldItalic.ttf"), {}, PASS),
        (
            TEST_FILE("cabin/Cabin-BoldItalic.ttf"),
            {NameID.FULL_FONT_NAME: "Make it fail"},
            FAIL,
        ),
        (TEST_FILE("abeezee/ABeeZee-Regular.ttf"), {}, PASS),
        # tests from test_check_name_typographicfamilyname
        (TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"), {}, PASS),
        (
            TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
            {NameID.TYPOGRAPHIC_FAMILY_NAME: "Arbitrary name"},
            FAIL,
        ),
        (TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"), {}, PASS),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
            {NameID.TYPOGRAPHIC_FAMILY_NAME: "Foo"},
            FAIL,
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
            {NameID.TYPOGRAPHIC_FAMILY_NAME: None},
            FAIL,
        ),
        # tests from test_check_name_typographicsubfamilyname
        (TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"), {}, PASS),
        (
            TEST_FILE("montserrat/Montserrat-BoldItalic.ttf"),
            {NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "Foo"},
            FAIL,
        ),
        (TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"), {}, PASS),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
            {NameID.TYPOGRAPHIC_SUBFAMILY_NAME: None},
            FAIL,
        ),
        (
            TEST_FILE("montserrat/Montserrat-ExtraLight.ttf"),
            {NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "Generic Name"},
            FAIL,
        ),
        # variable font checks
        (TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"), {}, PASS),
        # Open Sans' origin is Light so this should pass
        (
            TEST_FILE("varfont/OpenSans[wdth,wght].ttf"),
            {
                NameID.FONT_SUBFAMILY_NAME: "Regular",
                NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "Light",
            },
            PASS,
        ),
        (
            TEST_FILE("varfont/OpenSans[wdth,wght].ttf"),
            {
                NameID.FONT_SUBFAMILY_NAME: "Regular",
                NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "Condensed Light",
            },
            FAIL,
        ),
        (TEST_FILE("varfont/RobotoSerif[GRAD,opsz,wdth,wght].ttf"), {}, FAIL),
        # Roboto Serif has an opsz axes so this should pass
        (
            TEST_FILE("varfont/RobotoSerif[GRAD,opsz,wdth,wght].ttf"),
            {
                NameID.FONT_FAMILY_NAME: "Roboto Serif",
                NameID.FONT_SUBFAMILY_NAME: "Regular",
                NameID.FULL_FONT_NAME: "Roboto Serif Regular",
                NameID.POSTSCRIPT_NAME: "RobotoSerif-Regular",
                NameID.TYPOGRAPHIC_FAMILY_NAME: None,
                NameID.TYPOGRAPHIC_SUBFAMILY_NAME: None,
            },
            PASS,
        ),
        (TEST_FILE("varfont/Georama[wdth,wght].ttf"), {}, PASS),
        # Georama's default fvar vals are wdth=62.5, wght=100
        # which means ExtraCondensed Thin should appear in the family name
        (
            TEST_FILE("varfont/Georama[wdth,wght].ttf"),
            {
                NameID.FONT_FAMILY_NAME: "Georama ExtraCondensed Thin",
                NameID.FONT_SUBFAMILY_NAME: "Regular",
                NameID.TYPOGRAPHIC_FAMILY_NAME: "Georama",
                NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "ExtraCondensed Thin",
            },
            PASS,
        ),
    ],
)
def test_check_font_names(fp, mod, result):
    """Check font names are correct"""
    # Please note: This check was introduced in
    # https://github.com/fonttools/fontbakery/pull/3800 which has replaced
    # the following checks:
    #   com.google.fonts/check/name/familyname
    #   com.google.fonts/check/name/subfamilyname
    #   com.google.fonts/check/name/typographicfamilyname
    #   com.google.fonts/check/name/typographicsubfamilyname
    # It works by simply using the nametable builder which is found in the
    # axis registry,
    # https://github.com/googlefonts/axisregistry/blob/main/Lib/axisregistry/__init__.py#L232
    # this repository already has good unit tests but this check will also include the
    # previous test cases found in fontbakery.
    # https://github.com/googlefonts/axisregistry/blob/main/tests/test_names.py

    check = CheckTester("com.google.fonts/check/font_names")
    ttFont = TTFont(fp)
    # get the expecteed font names now before we modify them
    expected = expected_font_names(ttFont, [])
    if mod:
        for k, v in mod.items():
            if v is None:
                ttFont["name"].removeNames(k)
            else:
                ttFont["name"].setName(v, k, 3, 1, 0x409)

    if result == PASS:
        assert_PASS(
            check(MockFont(file=fp, ttFont=ttFont, expected_font_names=expected)),
            "with a good font...",
        )
    elif result == WARN:
        assert_results_contain(
            check(MockFont(file=fp, ttFont=ttFont, expected_font_names=expected)),
            WARN,
            "lacks-regular",
            "with bad names",
        )
    else:
        assert_results_contain(
            check(MockFont(file=fp, ttFont=ttFont, expected_font_names=expected)),
            FAIL,
            "bad-names",
            "with bad names",
        )


def test_check_name_mandatory_entries():
    """Font has all mandatory 'name' table entries ?"""
    check = CheckTester("com.google.fonts/check/name/mandatory_entries")

    # We'll check both RIBBI and non-RIBBI fonts
    # so that we cover both cases for FAIL/PASS scenarios

    # === First with a RIBBI font: ===
    # Our reference Cabin Regular is known to be good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good RIBBI font...")

    mandatory_entries = [
        NameID.FONT_FAMILY_NAME,
        NameID.FONT_SUBFAMILY_NAME,
        NameID.FULL_FONT_NAME,
        NameID.POSTSCRIPT_NAME,
    ]

    # then we "remove" each mandatory entry one by one:
    for mandatory in mandatory_entries:
        ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
        for i, name in enumerate(ttFont["name"].names):
            if name.nameID == mandatory:
                ttFont["name"].names[
                    i
                ].nameID = 0  # not really removing it, but replacing it
                # by something else completely irrelevant
                # for the purposes of this specific check
        assert_results_contain(
            check(ttFont),
            FAIL,
            "missing-entry",
            f"with a missing madatory (RIBBI) name entry (id={mandatory})...",
        )

    # === And now a non-RIBBI font: ===
    # Our reference Merriweather Black is known to be good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Black.ttf"))
    assert_PASS(check(ttFont), "with a good non-RIBBI font...")

    mandatory_entries = [
        NameID.FONT_FAMILY_NAME,
        NameID.FONT_SUBFAMILY_NAME,
        NameID.FULL_FONT_NAME,
        NameID.POSTSCRIPT_NAME,
        NameID.TYPOGRAPHIC_FAMILY_NAME,
        NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
    ]

    # then we (again) "remove" each mandatory entry one by one:
    for mandatory in mandatory_entries:
        ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Black.ttf"))
        for i, name in enumerate(ttFont["name"].names):
            if name.nameID in mandatory_entries:
                ttFont["name"].names[
                    i
                ].nameID = 0  # not really removing it, but replacing it
                # by something else completely irrelevant
                # for the purposes of this specific check
        assert_results_contain(
            check(ttFont),
            FAIL,
            "missing-entry",
            "with a missing madatory (non-RIBBI) name entry (id={mandatory})...",
        )


def test_condition_familyname_with_spaces():
    assert MockFont(familyname="OverpassMono").familyname_with_spaces == "Overpass Mono"
    assert (
        MockFont(familyname="BodoniModa11").familyname_with_spaces == "Bodoni Moda 11"
    )


def test_check_name_copyright_length():
    """Length of copyright notice must not exceed 500 characters."""
    check = CheckTester("com.google.fonts/check/name/copyright_length")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    good_entry = "a" * 499
    for i, entry in enumerate(ttFont["name"].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont["name"].names[i].string = good_entry.encode(entry.getEncoding())
    assert_PASS(check(ttFont), "with 499-byte copyright notice string...")

    good_entry = "a" * 500
    for i, entry in enumerate(ttFont["name"].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont["name"].names[i].string = good_entry.encode(entry.getEncoding())
    assert_PASS(check(ttFont), "with 500-byte copyright notice string...")

    bad_entry = "a" * 501
    for i, entry in enumerate(ttFont["name"].names):
        if entry.nameID == NameID.COPYRIGHT_NOTICE:
            ttFont["name"].names[i].string = bad_entry.encode(entry.getEncoding())
    assert_results_contain(
        check(ttFont), FAIL, "too-long", "with 501-byte copyright notice string..."
    )


# TODO: Maybe skip this code-test if the service is offline?
# we could use pytest.mak.skipif here together with a piece of code that
# verifies whether or not the namecheck.fontdata.com website is online at the moment
def test_check_fontdata_namecheck():
    """Familyname is unique according to namecheck.fontdata.com"""
    check = CheckTester("com.google.fonts/check/fontdata_namecheck")

    TIMEOUT_MSG = (
        "Sometimes namecheck.fontdata.com times out"
        " and we don't want to stop running all the other"
        " code tests. Unless you touched this portion of"
        " the code, it is generaly safe to ignore this glitch."
    )
    # We dont FAIL because this is meant as a merely informative check
    # There may be frequent cases when fonts are being updated and thus
    # already have a public family name registered on the
    # namecheck.fontdata.com database.
    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(
        check(font),
        INFO,
        "name-collision",
        "with an already used name...",
        ignore_error=TIMEOUT_MSG,
    )

    # Here we know that FamilySans has not been (and will not be)
    # registered as a real family.
    font = TEST_FILE("familysans/FamilySans-Regular.ttf")
    assert_PASS(check(font), "with a unique family name...", ignore_error=TIMEOUT_MSG)


def test_check_glyf_nested_components():
    """Check glyphs do not have nested components."""
    check = CheckTester("com.google.fonts/check/glyf_nested_components")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))
    assert_PASS(check(ttFont))

    # We need to create a nested component. "second" has components, so setting
    # one of "quotedbl"'s components to "second" should do it.
    ttFont["glyf"]["quotedbl"].components[0].glyphName = "second"

    assert_results_contain(check(ttFont), FAIL, "found-nested-components")


# Temporarily disabling this code-test since check/negative_advance_width itself
# is disabled waiting for an implementation targetting the
# actual root cause of the issue.
#
# See also comments at googlefons.py as well as at
# https://github.com/fonttools/fontbakery/issues/1727
def disabled_test_check_negative_advance_width():
    """Check that advance widths cannot be inferred as negative."""
    check = CheckTester("com.google.fonts/check/negative_advance_width")

    # Our reference Cabin Regular is good
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))

    # So it must PASS
    assert_PASS(check(ttFont), "with a good font...")

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
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-coordinates",
        "with bad coordinates on the glyf table...",
    )


def test_check_varfont_generate_static():
    """Check a static ttf can be generated from a variable font."""
    check = CheckTester("com.google.fonts/check/varfont/generate_static")

    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))
    assert_PASS(check(ttFont))

    # Mangle the coordinates of the first named instance
    # to deliberately break the variable font.
    ttFont["fvar"].instances[0].coordinates = {"fooo": 400.0, "baar": 100.0}
    msg = assert_results_contain(check(ttFont), FAIL, "varlib-mutator")
    assert "fontTools.varLib.mutator failed" in msg

    # Now delete the fvar table to exercise a SKIP result due an unfulfilled condition.
    del ttFont["fvar"]
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_variable_font" in msg


def test_check_varfont_has_HVAR():
    """Check that variable fonts have an HVAR table."""
    check = CheckTester("com.google.fonts/check/varfont/has_HVAR")

    # Our reference Cabin Variable Font contains an HVAR table.
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))

    # So the check must PASS.
    assert_PASS(check(ttFont))

    # Introduce the problem by removing the HVAR table:
    del ttFont["HVAR"]
    assert_results_contain(check(ttFont), FAIL, "lacks-HVAR")


def test_check_smart_dropout():
    """Font enables smart dropout control in "prep" table instructions?"""
    check = CheckTester("com.google.fonts/check/smart_dropout")

    ttFont = TTFont(TEST_FILE("nunito/Nunito-Regular.ttf"))

    # "Program at 'prep' table contains
    #  instructions enabling smart dropout control."
    assert_PASS(check(ttFont))

    # "Font does not contain TrueType instructions enabling
    #  smart dropout control in the 'prep' table program."
    import array

    ttFont["prep"].program.bytecode = array.array("B", [0])
    assert_results_contain(check(ttFont), FAIL, "lacks-smart-dropout")


def test_check_vttclean():
    """There must not be VTT Talk sources in the font."""
    check = CheckTester("com.google.fonts/check/vttclean")

    good_font = TEST_FILE("mada/Mada-Regular.ttf")
    assert_PASS(check(good_font))

    bad_font = TEST_FILE("hinting/Roboto-VF.ttf")
    assert_results_contain(check(bad_font), FAIL, "has-vtt-sources")


def test_check_aat():
    """Are there unwanted Apple tables ?"""
    check = CheckTester("com.google.fonts/check/aat")

    unwanted_tables = [
        "EBSC",
        "Zaph",
        "acnt",
        "ankr",
        "bdat",
        "bhed",
        "bloc",
        "bmap",
        "bsln",
        "fdsc",
        "feat",
        "fond",
        "gcid",
        "just",
        "kerx",
        "lcar",
        "ltag",
        "mort",
        "morx",
        "opbd",
        "prop",
        "trak",
        "xref",
    ]
    # Our reference Mada Regular font is good here:
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # We now add unwanted tables one-by-one to validate the FAIL code-path:
    for unwanted in unwanted_tables:
        ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
        ttFont.reader.tables[unwanted] = "foo"
        assert_results_contain(
            check(ttFont),
            FAIL,
            "has-unwanted-tables",
            f"with unwanted table {unwanted} ...",
        )


def test_check_fvar_name_entries():
    """All name entries referenced by fvar instances exist on the name table?"""
    # TODO fix
    check = CheckTester("com.google.fonts/check/fvar_instances")

    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # rename the first fvar instance so the font is broken
    ttFont["name"].setName("foo", 258, 3, 1, 0x409)

    # So it must FAIL the check:
    assert_results_contain(
        check(ttFont), FAIL, "bad-fvar-instances", "with a bad font..."
    )

    # rename the first fvar instance so it is correct
    ttFont["name"].setName("Regular", 258, 3, 1, 0x409)

    assert_PASS(check(ttFont), "with a good font...")


def test_check_varfont_has_instances():
    """A variable font must have named instances."""
    # TODO Fix!
    check = CheckTester("com.google.fonts/check/fvar_instances")

    # ExpletusVF does have instances.
    # Note: The "broken" in the path name refers to something else.
    #       (See test_check_fvar_name_entries)
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    # If we delete all instances, then it must FAIL:
    while len(ttFont["fvar"].instances):
        del ttFont["fvar"].instances[0]

    assert_results_contain(
        check(ttFont), FAIL, "bad-fvar-instances", "with a bad font..."
    )


def test_check_varfont_weight_instances():
    """Variable font weight coordinates must be multiples of 100."""
    check = CheckTester("com.google.fonts/check/fvar_instances")

    # This copy of Markazi Text has an instance with
    # a 491 'wght' coordinate instead of 500.
    ttFont = TTFont(TEST_FILE("broken_markazitext/MarkaziText-VF.ttf"))

    # So it must FAIL the check:
    assert_results_contain(
        check(ttFont), FAIL, "bad-fvar-instances", "with a bad font..."
    )

    # Let's then change the weight coordinates to make it PASS the check:
    # instances are from 400-700 (Regular-Bold) so set start to 400
    wght_val = 400
    for i, instance in enumerate(ttFont["fvar"].instances):
        ttFont["fvar"].instances[i].coordinates["wght"] = wght_val
        wght_val += 100

    assert_PASS(check(ttFont), "with a good font...")


def NOT_IMPLEMENTED_test_check_family_tnum_horizontal_metrics():
    """All tabular figures must have the same width across the RIBBI-family."""
    # check = CheckTester( "com.google.fonts/check/family/tnum_horizontal_metrics")
    # TODO: Implement-me!
    #
    # code-paths:
    # - FAIL, "inconsistent-widths"
    # - PASS


def test_check_integer_ppem_if_hinted():
    """PPEM must be an integer on hinted fonts."""
    check = CheckTester("com.google.fonts/check/integer_ppem_if_hinted")

    # Our reference Merriweather Regular is hinted, but does not set
    # the "rounded PPEM" flag (bit 3 on the head table flags) as
    # described at https://docs.microsoft.com/en-us/typography/opentype/spec/head
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # So it must FAIL the check:
    assert_results_contain(check(ttFont), FAIL, "bad-flags", "with a bad font...")

    # hotfixing it should make it PASS:
    ttFont["head"].flags |= 1 << 3

    assert_PASS(check(ttFont), "with a good font...")


def test_check_ligature_carets():
    """Is there a caret position declared for every ligature?"""
    check = CheckTester("com.google.fonts/check/ligature_carets")

    # Our reference Mada Medium doesn't have a GSUB 'liga' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: ligature_glyphs" in msg

    # Simulate an error coming from the 'ligature_glyphs' condition;
    # this is to exercise the 'malformed' code path.
    font = TEST_FILE("mada/Mada-Medium.ttf")
    msg = assert_results_contain(
        check(MockFont(file=font, ligature_glyphs=-1)), FAIL, "malformed"
    )
    assert "Failed to lookup ligatures. This font file seems to be malformed." in msg

    # SourceSansPro Bold has ligatures and GDEF table, but lacks caret position data.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    msg = assert_results_contain(check(ttFont), WARN, "lacks-caret-pos")
    assert msg == (
        "This font lacks caret position values"
        " for ligature glyphs on its GDEF table."
    )

    # Remove the GDEF table to exercise the 'GDEF-missing' code path.
    del ttFont["GDEF"]
    msg = assert_results_contain(check(ttFont), WARN, "GDEF-missing")
    assert "GDEF table is missing, but it is mandatory" in msg

    # TODO: test the following code-paths:
    # - WARN "incomplete-caret-pos-data"
    # - PASS (We currently lack a reference family that PASSes this check!)


def test_check_kerning_for_non_ligated_sequences():
    """Is there kerning info for non-ligated sequences ?"""
    check = CheckTester("com.google.fonts/check/kerning_for_non_ligated_sequences")

    # Our reference Mada Medium doesn't have a GSUB 'liga' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("mada/Mada-Medium.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: ligatures" in msg

    # Simulate an error coming from the 'ligatures' condition;
    # this is to exercise the 'malformed' code path.
    font = TEST_FILE("mada/Mada-Medium.ttf")
    msg = assert_results_contain(
        check(MockFont(file=font, ligatures=-1)), FAIL, "malformed"
    )
    assert "Failed to lookup ligatures. This font file seems to be malformed." in msg

    # And Merriweather Regular doesn't have a GPOS 'kern' feature, so it is skipped
    # because of an unfulfilled condition.
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: has_kerning_info" in msg

    # SourceSansPro Bold is known to not kern the non-ligated glyph sequences.
    ttFont = TTFont(TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf"))
    msg = assert_results_contain(check(ttFont), WARN, "lacks-kern-info")
    assert msg == (
        "GPOS table lacks kerning info for the following non-ligated sequences:\n\n"
        "\t- f + f\n\n\t- f + t"
    )

    # Simulate handling of multi-component ligatures
    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Bold.otf")
    msg = assert_results_contain(
        check(MockFont(file=font, ligatures={"f": [["f", "i"], ["f", "l"]]})),
        WARN,
        "lacks-kern-info",
    )
    assert msg == (
        "GPOS table lacks kerning info for the following non-ligated sequences:\n\n"
        "\t- f + f\n\n\t- f + i\n\n\t- f + l"
    )


def test_check_family_control_chars():
    """Are any unacceptable control characters present in font files?"""
    check = CheckTester("com.google.fonts/check/family/control_chars")

    good_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCGood-Regular.ttf"
    )
    onebad_cc_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCOneBad-Regular.ttf"
    )
    multibad_cc_font = TEST_FILE(
        "bad_character_set/control_chars/FontbakeryTesterCCMultiBad-Regular.ttf"
    )

    # No unacceptable control characters should pass with one file
    fonts = [good_font]
    assert_PASS(check(fonts), "with one good font...")

    # No unacceptable control characters should pass with multiple good files
    fonts = [good_font, good_font]
    assert_PASS(check(fonts), "with multiple good fonts...")

    # Unacceptable control chars should fail with one file x one bad char in font
    fonts = [onebad_cc_font]
    assert_results_contain(
        check(fonts), FAIL, "unacceptable", "with one bad font that has one bad char..."
    )

    # Unacceptable control chars should fail with one file x multiple bad char in font
    fonts = [multibad_cc_font]
    assert_results_contain(
        check(fonts),
        FAIL,
        "unacceptable",
        "with one bad font that has multiple bad char...",
    )

    # Unacceptable control chars should fail with multiple files x multiple bad chars
    # in fonts
    fonts = [onebad_cc_font, multibad_cc_font]
    assert_results_contain(
        check(fonts),
        FAIL,
        "unacceptable",
        "with multiple bad fonts that have multiple bad chars...",
    )


def test_check_family_italics_have_roman_counterparts():
    """Ensure Italic styles have Roman counterparts."""
    check = CheckTester(
        "com.google.fonts/check/family/italics_have_roman_counterparts",
    )

    # The path used here, "some-crazy.path/", is meant to ensure
    # that the parsing code does not get lost when trying to
    # extract the style of a font file.
    fonts = [
        "some-crazy.path/merriweather/Merriweather-BlackItalic.ttf",
        "some-crazy.path/merriweather/Merriweather-Black.ttf",
        "some-crazy.path/merriweather/Merriweather-BoldItalic.ttf",
        "some-crazy.path/merriweather/Merriweather-Bold.ttf",
        "some-crazy.path/merriweather/Merriweather-Italic.ttf",
        "some-crazy.path/merriweather/Merriweather-LightItalic.ttf",
        "some-crazy.path/merriweather/Merriweather-Light.ttf",
        "some-crazy.path/merriweather/Merriweather-Regular.ttf",
    ]

    assert_PASS(check([MockFont(file=font) for font in fonts]), "with a good family...")

    fonts.pop(-1)  # remove the last one, which is the Regular
    assert "some-crazy.path/merriweather/Merriweather-Regular.ttf" not in fonts
    assert "some-crazy.path/merriweather/Merriweather-Italic.ttf" in fonts
    assert_results_contain(
        check(fonts),
        FAIL,
        "missing-roman",
        "with a family that has an Italic but lacks a Regular.",
    )

    fonts.append("some-crazy.path/merriweather/MerriweatherItalic.ttf")
    assert_results_contain(
        check(fonts),
        WARN,
        "bad-filename",
        "with a family that has a non-canonical italic filename.",
    )

    # This check must also be able to deal with variable fonts!
    fonts = [
        "cabinvfbeta/CabinVFBeta-Italic[wdth,wght].ttf",
        "cabinvfbeta/CabinVFBeta[wdth,wght].ttf",
    ]
    assert_PASS(check(fonts), "with a good set of varfonts...")

    fonts = ["cabinvfbeta/CabinVFBeta-Italic[wdth,wght].ttf"]
    assert_results_contain(
        check(fonts),
        FAIL,
        "missing-roman",
        "with an Italic varfont that lacks a Roman counterpart.",
    )


def test_check_repo_dirname_match_nameid_1(tmp_path):
    check = CheckTester("com.google.fonts/check/repo/dirname_matches_nameid_1")
    FONT_FAMILY_NAME = "rosarivo"

    # Create a temporary directory that mimics the folder structure of the Google Fonts
    # repository, and copy into it a test family that is known to have all the necessary
    # files.
    tmp_gf_dir = tmp_path / f"ofl/{FONT_FAMILY_NAME}"
    src_family = portable_path(f"data/test/{FONT_FAMILY_NAME}")
    shutil.copytree(src_family, tmp_gf_dir, dirs_exist_ok=True)

    # PASS result
    fonts = [str(pth) for pth in tmp_gf_dir.glob("*.ttf")]
    assert_PASS(check(fonts))

    # Get the path of the Regular font; it will be used for deleting the file later.
    reg_font_path = next((pth for pth in fonts if "Regular" in pth), None)

    # Now rename the temporary directory to make the check fail.
    new_dir_name = f"not_{FONT_FAMILY_NAME}"
    renamed_tmp_gf_dir = tmp_gf_dir.with_name(new_dir_name)
    os.replace(tmp_gf_dir, renamed_tmp_gf_dir)

    # FAIL ("mismatch") result
    fonts = [str(pth) for pth in renamed_tmp_gf_dir.glob("*.ttf")]
    msg = assert_results_contain(check(fonts), FAIL, "mismatch")
    assert msg == (
        f"Family name on the name table ('{FONT_FAMILY_NAME.title()}')"
        f" does not match directory name in the repo structure ('{new_dir_name}')."
        f" Expected '{FONT_FAMILY_NAME}'."
    )

    # Rename the temporary directory back to the original name,
    # and delete the Regular font file to make the check fail.
    os.replace(renamed_tmp_gf_dir, tmp_gf_dir)
    os.remove(reg_font_path)

    # FAIL ("lacks-regular") result
    fonts = [str(pth) for pth in tmp_gf_dir.glob("*.ttf")]
    msg = assert_results_contain(check(fonts), FAIL, "lacks-regular")
    assert "The font seems to lack a regular." in msg

    # SKIP result; the fonts are in a directory that doesn't have the correct structure.
    msg = assert_results_contain(check(cabin_fonts), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: gfonts_repo_structure" in msg


def test_check_repo_vf_has_static_fonts(tmp_path):
    """Check VF family dirs in google/fonts contain static fonts"""
    check = CheckTester("com.google.fonts/check/repo/vf_has_static_fonts")

    # in order for this check to work, we need to
    # mimic the folder structure of the Google Fonts repository
    dir_path = "ofl/foo/bar"
    tmp_gf_dir = tmp_path / "repo_vf_has_static_fonts"
    tmp_gf_dir.mkdir()
    family_dir = tmp_gf_dir / "ofl/testfamily"
    src_family = portable_path("data/test/varfont")

    shutil.copytree(src_family, family_dir, dirs_exist_ok=True)

    assert_PASS(
        check(MockFont(file=family_dir / "foo", family_directory=family_dir)),
        "for a VF family which does not have a static dir.",
    )

    static_dir = family_dir / "static"
    static_dir.mkdir()
    static_fonts = portable_path("data/test/ibmplexsans-vf")
    shutil.rmtree(static_dir)
    shutil.copytree(static_fonts, static_dir)
    assert_PASS(
        check(MockFont(file=family_dir / "foo", family_directory=family_dir)),
        "for a VF family which has a static dir and manually hinted static fonts",
    )

    static_fonts = portable_path("data/test/overpassmono")
    shutil.rmtree(static_dir)
    static_dir.mkdir()
    shutil.copyfile(
        os.path.join(static_fonts, "OverpassMono-Regular.ttf"),
        static_dir / "OverpassMono-Regular.ttf",
    )

    assert_results_contain(
        check(MockFont(file=family_dir / "foo", family_directory=family_dir)),
        WARN,
        "not-manually-hinted",
        "for a VF family which has a static dir but no manually hinted static fonts",
    )


def test_check_repo_upstream_yaml_has_required_fields():
    """Check upstream.yaml has all required fields"""
    check = CheckTester(
        "com.google.fonts/check/repo/upstream_yaml_has_required_fields",
    )
    upstream_yaml = {
        "branch": "main",
        "files": {"TestFamily-Regular.ttf": "TestFamily-Regular.ttf"},
    }
    # Pass if upstream.yaml file contains all fields
    assert_PASS(
        check(MockFont(upstream_yaml=upstream_yaml)),
        "for an upstream.yaml which contains all fields",
    )

    # Fail if it doesn't
    upstream_yaml.pop("files")
    assert_results_contain(
        check(MockFont(upstream_yaml=upstream_yaml)),
        FAIL,
        "missing-fields",
        "for an upsream.yaml which doesn't contain all fields",
    )


def test_check_repo_fb_report(tmp_path):
    """A font repository should not include FontBakery report files"""
    check = CheckTester("com.google.fonts/check/repo/fb_report")

    family_dir = tmp_path / "repo_fb_report"
    family_dir.mkdir()
    src_family = portable_path("data/test/varfont")

    shutil.copytree(src_family, family_dir, dirs_exist_ok=True)

    assert_PASS(
        check(MockFont(family_directory=family_dir)),
        "for a repo without FontBakery report files.",
    )

    assert_PASS(
        check(MockFont(family_directory=family_dir)),
        "with a json file that is not a FontBakery report.",
    )

    # Add a json file that is not a FB report
    open(os.path.join(family_dir, "something_else.json"), "w+", encoding="utf-8").write(
        "this is not a FB report"
    )

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
    # Report files must be detected even if placed on subdirectories and the check code
    # should not rely only on filename (such as "Jura-Regular.fb-report.json")
    # but should instead inspect the contents of the file:
    open(
        os.path.join(family_dir, "jura", "static", "my_fontfamily_name.json"),
        "w+",
        encoding="utf-8",
    ).write(FB_REPORT_SNIPPET)
    assert_results_contain(
        check(MockFont(family_directory=family_dir)),
        WARN,
        "fb-report",
        "with an actual snippet of a report.",
    )


def test_check_repo_zip_files(tmp_path):
    """A font repository should not include ZIP files"""
    check = CheckTester("com.google.fonts/check/repo/zip_files")

    family_dir = tmp_path / "repo_zip_files"
    family_dir.mkdir()
    src_family = portable_path("data/test/varfont")

    shutil.copytree(src_family, family_dir, dirs_exist_ok=True)

    assert_PASS(
        check(MockFont(family_directory=family_dir)), "for a repo without ZIP files."
    )

    for ext in ["zip", "rar", "7z"]:
        # ZIP files must be detected even if placed on subdirectories:
        filepath = os.path.join(family_dir, "jura", "static", f"fonts-release.{ext}")
        # create an empty file. The check won't care about the contents:
        open(filepath, "w+", encoding="utf-8")
        assert_results_contain(
            check(MockFont(family_directory=family_dir)),
            FAIL,
            "zip-files",
            f"when a {ext} file is found.",
        )
        # remove the file before testing the next one ;-)
        os.remove(filepath)


def test_check_vertical_metrics():
    check = CheckTester("com.google.fonts/check/vertical_metrics")

    font = TEST_FILE("akshar/Akshar[wght].ttf")

    msg = assert_results_contain(check(font), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: not remote_styles" in msg

    # Defeat the 'not remote_styles' condition.
    # linegap is not 0
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False)),
        FAIL,
        "bad-hhea.lineGap",
        'hhea.lineGap is "150" it should be 0',
    )
    ttFont = TTFont(font)

    # hhea sum is above 2000 -> FAIL
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 0
    ttFont["hhea"].descent = -2000
    ttFont["OS/2"].sTypoDescender = -2000
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "bad-hhea-range",
        "hhea sum is above 2000",
    )

    # hhea sum is below 1200 -> FAIL
    ttFont["hhea"].descent = 0
    ttFont["OS/2"].sTypoDescender = 0
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "bad-hhea-range",
        "hhea sum is below 1200",
    )

    # hhea sum is above 1500 -> WARN
    ttFont["hhea"].descent = -700
    ttFont["OS/2"].sTypoDescender = -700
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        WARN,
        "bad-hhea-range",
        "hhea sum is above 1500",
    )

    # hhea sum is in range
    ttFont["hhea"].descent = -300
    ttFont["OS/2"].sTypoDescender = -300
    assert_PASS(check(MockFont(file=font, remote_styles=False, ttFont=ttFont)))

    # reset
    def reset_metrics():
        ttFont["hhea"].ascent = 900
        ttFont["hhea"].descent = -300
        ttFont["OS/2"].sTypoAscender = 900
        ttFont["OS/2"].sTypoDescender = -300
        ttFont["hhea"].lineGap = 0
        ttFont["OS/2"].sTypoLineGap = 0
        ttFont["OS/2"].usWinAscent = 900
        ttFont["OS/2"].usWinDescent = 300

    # ascenders are negative -> FAIL
    reset_metrics()
    ttFont["OS/2"].sTypoAscender = -900
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "typo-ascender",
        "typo ascender is negative",
    )
    reset_metrics()
    ttFont["hhea"].ascent = -900
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "hhea-ascent",
        "hhea ascent is negative",
    )

    # descenders are positive -> FAIL
    reset_metrics()
    ttFont["OS/2"].sTypoDescender = 300
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "typo-descender",
        "typo descender is positive",
    )
    reset_metrics()
    ttFont["hhea"].descent = 300
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "hhea-descent",
        "hhea descent is positive",
    )

    # winascent is negative -> FAIL
    reset_metrics()
    ttFont["OS/2"].usWinAscent = -900
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "win-ascent",
        "OS/2.usWinAscent is negative",
    )

    # windescent is negative -> FAIL
    reset_metrics()
    ttFont["OS/2"].usWinDescent = -300
    assert_results_contain(
        check(MockFont(file=font, remote_styles=False, ttFont=ttFont)),
        FAIL,
        "win-descent",
        "OS/2.usWinDescent is negative",
    )


def test_check_vertical_metrics_regressions():
    check = CheckTester("com.google.fonts/check/vertical_metrics_regressions")

    def new_context():
        context = MockContext(
            testables=[Font(x) for x in cabin_fonts], config={"skip_network": False}
        )
        for testable in context.testables:
            testable.context = context
        return context

    # Cabin test family should match by default
    context = new_context()
    assert_PASS(check(context), "with a good family...")

    # FAIL with changed vertical metric values
    local_regular = context.regular_ttFont
    local_regular["OS/2"].sTypoAscender = 0
    context.regular_ttFont = local_regular
    assert_results_contain(
        check(context),
        FAIL,
        "bad-typo-ascender",
        "with a family which has an incorrect typoAscender...",
    )

    local_regular["OS/2"].sTypoDescender = 0
    assert_results_contain(
        check(context),
        FAIL,
        "bad-typo-descender",
        "with a family which has an incorrect typoDescender...",
    )

    local_regular["hhea"].ascent = 0
    assert_results_contain(
        check(context),
        FAIL,
        "bad-hhea-ascender",
        "with a family which has an incorrect hhea ascender...",
    )

    local_regular["hhea"].descent = 0
    assert_results_contain(
        check(context),
        FAIL,
        "bad-hhea-descender",
        "with a family which has an incorrect hhea descender...",
    )

    # Fail if family on Google Fonts has fsSelection bit 7 enabled
    # but checked fonts don't
    local_regular["OS/2"].fsSelection &= ~(1 << 7)
    assert_results_contain(
        check(context),
        FAIL,
        "bad-fsselection-bit7",
        "with a remote family which has typo metrics "
        "enabled and the fonts being checked don't.",
    )

    if 0:  # FIXME: pylint:disable=W0125
        # Pass if family on Google Fonts doesn't have fsSelection bit 7 enabled
        # but checked fonts have taken this into consideration
        context = new_context()
        remote_regular = context.testables[0].regular_remote_style
        local_regular = context.regular_ttFont

        remote_regular["OS/2"].fsSelection &= ~(1 << 7)
        local_regular["OS/2"].sTypoAscender = remote_regular["OS/2"].usWinAscent
        local_regular["OS/2"].sTypoDescender = -remote_regular["OS/2"].usWinDescent
        local_regular["hhea"].ascent = remote_regular["OS/2"].usWinAscent
        local_regular["hhea"].descent = -remote_regular["OS/2"].usWinDescent
        context.regular_ttFont = local_regular
        context.regular_remote_style = remote_regular
        assert_PASS(
            check(context),
            "with a remote family which does not have typo metrics"
            " enabled but the checked fonts vertical metrics have been"
            " set so its typo and hhea metrics match the remote"
            " fonts win metrics.",
        )

    if 0:  # FIXME: pylint:disable=W0125
        # Same as previous check but using a remote font which has a different upm
        context = new_context()
        remote_regular = context.testables[0].regular_remote_style
        local_regular = context.regular_ttFont

        remote_regular["OS/2"].fsSelection &= ~(1 << 7)
        remote_regular["head"].unitsPerEm = 2000
        # divide by 2 since we've doubled the upm
        local_regular["OS/2"].sTypoAscender = math.ceil(
            remote_regular["OS/2"].usWinAscent / 2
        )
        local_regular["OS/2"].sTypoDescender = math.ceil(
            -remote_regular["OS/2"].usWinDescent / 2
        )
        local_regular["hhea"].ascent = math.ceil(remote_regular["OS/2"].usWinAscent / 2)
        local_regular["hhea"].descent = math.ceil(
            -remote_regular["OS/2"].usWinDescent / 2
        )
        context.regular_ttFont = local_regular
        context.regular_remote_style = remote_regular
        assert_PASS(
            check(context),
            "with a remote family which does not have typo metrics "
            "enabled but the checked fonts vertical metrics have been "
            "set so its typo and hhea metrics match the remote "
            "fonts win metrics.",
        )

    context = new_context()
    remote_regular = context.testables[0].regular_remote_style
    local_regular = context.regular_ttFont
    local_regular["OS/2"].fsSelection &= ~(1 << 7)
    context.local_regular = local_regular
    assert_results_contain(
        check(context),
        FAIL,
        "bad-fsselection-bit7",
        "OS/2 fsSelection bit 7 must be enabled.",
    )

    # Disable bit 7 in both fonts but change win metrics of ttFont
    context = new_context()
    remote_regular = context.testables[0].regular_remote_style
    local_regular = context.regular_ttFont

    remote_regular["OS/2"].fsSelection &= ~(1 << 7)
    local_regular["OS/2"].fsSelection &= ~(1 << 7)
    local_regular["OS/2"].usWinAscent = 2500
    context.local_regular = local_regular
    context.regular_remote_style = remote_regular

    assert_results_contain(
        check(context),
        FAIL,
        "bad-fsselection-bit7",
        "OS/2 fsSelection bit 7 must be enabled.",
    )


def test_check_cjk_vertical_metrics():
    check = CheckTester("com.google.fonts/check/cjk_vertical_metrics")

    ttFont = TTFont(cjk_font)
    assert_PASS(check(ttFont), "for Source Han Sans")

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].fsSelection |= 1 << 7
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-fselection-bit7",
        "for font where OS/2 fsSelection bit 7 is enabled",
    )

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].sTypoAscender = float("inf")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-OS/2.sTypoAscender",
        "for font with bad OS/2.sTypoAscender",
    )

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].sTypoDescender = float("inf")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-OS/2.sTypoDescender",
        "for font with bad OS/2.sTypoDescender",
    )

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].sTypoLineGap = float("inf")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-OS/2.sTypoLineGap",
        "for font where linegaps have been set (OS/2 table)",
    )

    ttFont = TTFont(cjk_font)
    ttFont["hhea"].lineGap = float("inf")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-hhea.lineGap",
        "for font where linegaps have been set (hhea table)",
    )

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].usWinAscent = float("inf")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "ascent-mismatch",
        "for a font where typo ascender != 0.88 * upm",
    )

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].usWinDescent = -float("inf")
    assert_results_contain(
        check(ttFont),
        FAIL,
        "descent-mismatch",
        "for a font where typo descender != 0.12 * upm",
    )

    ttFont = TTFont(cjk_font)
    ttFont["OS/2"].usWinAscent = float("inf")
    ttFont["hhea"].ascent = float("inf")
    assert_results_contain(
        check(ttFont),
        WARN,
        "bad-hhea-range",
        "if font hhea and win metrics are greater than 1.5 * upm",
    )


def test_check_cjk_vertical_metrics_regressions():
    # TODO: try to remove deepcopy usage
    from copy import deepcopy

    check = CheckTester("com.google.fonts/check/cjk_vertical_metrics_regressions")

    ttFont = TTFont(cjk_font)
    regular_remote_style = deepcopy(ttFont)

    # Check on duplicate
    regular_remote_style = deepcopy(ttFont)
    assert_PASS(
        check(MockFont(ttFont=ttFont, regular_remote_style=regular_remote_style)),
        "for Source Han Sans",
    )

    # Change a single metric
    ttFont2 = deepcopy(ttFont)
    ttFont2["hhea"].ascent = 0
    assert_results_contain(
        check(MockFont(ttFont=ttFont2, regular_remote_style=regular_remote_style)),
        FAIL,
        "cjk-metric-regression",
        "hhea ascent is 0 when it should be 880",
    )

    # Change upm of font being checked
    ttFont3 = deepcopy(ttFont)
    ttFont3["head"].unitsPerEm = 2000
    assert_results_contain(
        check(MockFont(ttFont=ttFont3, regular_remote_style=regular_remote_style)),
        FAIL,
        "cjk-metric-regression",
        "upm is 2000 and vert metrics values are not updated",
    )

    # Change upm of checked font and update vert metrics
    ttFont4 = deepcopy(ttFont)
    ttFont4["head"].unitsPerEm = 2000
    for tbl, attrib in [
        ("OS/2", "sTypoAscender"),
        ("OS/2", "sTypoDescender"),
        ("OS/2", "sTypoLineGap"),
        ("OS/2", "usWinAscent"),
        ("OS/2", "usWinDescent"),
        ("hhea", "ascent"),
        ("hhea", "descent"),
        ("hhea", "lineGap"),
    ]:
        current_val = getattr(ttFont4[tbl], attrib)
        setattr(ttFont4[tbl], attrib, current_val * 2)
    assert_PASS(
        check(MockFont(ttFont=ttFont4, regular_remote_style=regular_remote_style)),
        "for Source Han Sans with doubled upm and doubled vert metrics",
    )


def test_check_cjk_not_enough_glyphs():
    check = CheckTester("com.google.fonts/check/cjk_not_enough_glyphs")
    ttFont = TTFont(cjk_font)
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("montserrat/Montserrat-Regular.ttf"))
    msg = assert_results_contain(check(ttFont), SKIP, "unfulfilled-conditions")
    assert "Unfulfilled Conditions: is_claiming_to_be_cjk_font" in msg

    # Let's modify Montserrat's cmap so there's a cjk glyph
    cmap = ttFont["cmap"].getcmap(3, 1)
    # Add first character of the CJK unified Ideographs
    cmap.cmap[0x4E00] = "A"
    # And let's declare that we are a CJK font
    ttFont["OS/2"].ulCodePageRange1 |= 1 << 17

    msg = assert_results_contain(check(ttFont), WARN, "cjk-not-enough-glyphs")
    assert msg.startswith("There is only one CJK glyph")

    # Add second character of the CJK unified Ideographs
    cmap.cmap[0x4E01] = "B"
    msg = assert_results_contain(check(ttFont), WARN, "cjk-not-enough-glyphs")
    assert msg.startswith("There are only 2 CJK glyphs")


def test_check_varfont_instance_coordinates(vf_ttFont):
    check = CheckTester("com.google.fonts/check/fvar_instances")

    # OpenSans-Roman-VF is correct
    assert_PASS(
        check(vf_ttFont), "with a variable font which has correct instance coordinates."
    )

    from copy import copy

    vf_ttFont2 = copy(vf_ttFont)
    for instance in vf_ttFont2["fvar"].instances:
        for axis in instance.coordinates.keys():
            instance.coordinates[axis] = 0
    assert_results_contain(
        check(vf_ttFont2),
        FAIL,
        "bad-fvar-instances",
        "with a variable font which does not have correct instance coordinates.",
    )


def test_check_varfont_instance_names(vf_ttFont):
    check = CheckTester("com.google.fonts/check/fvar_instances")

    assert_PASS(
        check(vf_ttFont), "with a variable font which has correct instance names."
    )

    from copy import copy

    vf_ttFont2 = copy(vf_ttFont)
    for instance in vf_ttFont2["fvar"].instances:
        instance.subfamilyNameID = 300
    broken_name = "ExtraBlack Condensed 300pt"
    vf_ttFont2["name"].setName(
        broken_name,
        300,
        PlatformID.MACINTOSH,
        MacintoshEncodingID.ROMAN,
        MacintoshLanguageID.ENGLISH,
    )
    vf_ttFont2["name"].setName(
        broken_name,
        300,
        PlatformID.WINDOWS,
        WindowsEncodingID.UNICODE_BMP,
        WindowsLanguageID.ENGLISH_USA,
    )
    assert_results_contain(
        check(vf_ttFont2),
        FAIL,
        "bad-fvar-instances",
        "with a variable font which does not have correct instance names.",
    )


def test_check_varfont_duplicate_instance_names(vf_ttFont):
    check = CheckTester("com.google.fonts/check/varfont_duplicate_instance_names")

    assert_PASS(
        check(vf_ttFont), "with a variable font which has unique instance names."
    )

    from copy import copy

    vf_ttFont2 = copy(vf_ttFont)
    duplicate_instance_name = (
        vf_ttFont2["name"]
        .getName(
            vf_ttFont2["fvar"].instances[0].subfamilyNameID,
            PlatformID.WINDOWS,
            WindowsEncodingID.UNICODE_BMP,
            WindowsLanguageID.ENGLISH_USA,
        )
        .toUnicode()
    )
    vf_ttFont2["name"].setName(
        string=duplicate_instance_name,
        nameID=vf_ttFont2["fvar"].instances[1].subfamilyNameID,
        platformID=PlatformID.WINDOWS,
        platEncID=WindowsEncodingID.UNICODE_BMP,
        langID=WindowsLanguageID.ENGLISH_USA,
    )
    assert_results_contain(check(vf_ttFont2), FAIL, "duplicate-instance-names")

    # Change the nameID of the 3rd named instance to 456,
    # and don't create a name record with that nameID.
    name_id = 456
    vf_ttFont2["fvar"].instances[2].subfamilyNameID = name_id
    msg = assert_results_contain(check(vf_ttFont2), FAIL, "name-record-not-found")
    assert f" and nameID {name_id} was not found." in msg


def test_check_varfont_unsupported_axes():
    """Ensure VFs do not contain opsz or ital axes."""
    check = CheckTester("com.google.fonts/check/varfont/unsupported_axes")

    # Our reference varfont, CabinVFBeta.ttf, lacks 'ital' and 'slnt' variation axes.
    # So, should pass the check:
    ttFont = TTFont(TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"))
    assert_PASS(check(ttFont))

    # If we add 'ital' it must FAIL:
    from fontTools.ttLib.tables._f_v_a_r import Axis

    new_axis = Axis()
    new_axis.axisTag = "ital"
    ttFont["fvar"].axes.append(new_axis)
    assert_results_contain(check(ttFont), FAIL, "unsupported-ital")


def test_check_varfont_duplexed_axis_reflow():
    """Ensure VFs with the GRAD axis do not vary horizontal advance."""
    check = CheckTester("com.google.fonts/check/varfont/duplexed_axis_reflow")

    ttFont = TTFont(TEST_FILE("BadGrades/BadGrades-VF.ttf"))
    assert_results_contain(check(ttFont), FAIL, "grad-causes-reflow")

    # Zero out the horizontal advances
    gvar = ttFont["gvar"]
    for glyph, deltas in gvar.variations.items():
        for delta in deltas:
            if "GRAD" not in delta.axes:
                continue
            if delta.coordinates:
                delta.coordinates = delta.coordinates[:-4] + [(0, 0)] * 4

    # But the kern rules should still be a problem
    assert_results_contain(check(ttFont), FAIL, "duplexed-kern-causes-reflow")

    ttFont["GPOS"].table.LookupList.Lookup = []
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("bad_fonts/reflowing_ROND/BadRoundness-VF.ttf"))
    assert_results_contain(check(ttFont), FAIL, "rond-causes-reflow")


def test_check_gfaxisregistry_bounds():
    """Validate METADATA.pb axes values are within gf_axisregistry bounds."""
    check = CheckTester("com.google.fonts/check/metadata/gf_axisregistry_bounds")

    # Our reference varfont, CabinVF, has good axes bounds:
    font = TEST_FILE("cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(font))

    # The first axis declared in this family is 'wdth' (Width)
    # And the GF Axis Registry expects this axis to have a range
    # not broader than min: 25 / max: 200
    # So...
    md = Font(font).family_metadata
    md.axes[0].min_value = 20
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "bad-axis-range"
    )

    md.axes[0].min_value = 25
    md.axes[0].max_value = 250
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "bad-axis-range"
    )


def test_check_gf_axisregistry_valid_tags():
    """Validate METADATA.pb axes tags are defined in gf_axisregistry."""
    check = CheckTester(
        "com.google.fonts/check/metadata/gf_axisregistry_valid_tags",
    )

    # The axis tags in our reference varfont, CabinVF,
    # are properly defined in the registry:
    font = TEST_FILE("cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(font))

    md = Font(font).family_metadata
    md.axes[
        0
    ].tag = "crap"  # I'm pretty sure this one wont ever be included in the registry
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "bad-axis-tag"
    )


def test_check_gf_axisregistry_fvar_axis_defaults():
    """Validate METADATA.pb axes tags are defined in gf_axisregistry."""
    check = CheckTester("com.google.fonts/check/gf_axisregistry/fvar_axis_defaults")

    # The default value for the axes in this reference varfont
    # are properly registered in the registry:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_PASS(check(ttFont))

    # And this value surely doen't map to a fallback name in the registry
    ttFont["fvar"].axes[0].defaultValue = 123
    assert_results_contain(check(ttFont), FAIL, "not-registered")


def test_check_STAT_gf_axisregistry():
    """
    Validate STAT particle names and values match the fallback names in GFAxisRegistry.
    """
    check = CheckTester("com.google.fonts/check/STAT/gf_axisregistry")

    # Our reference varfont, CabinVF,
    # has "Regular", instead of "Roman" in its 'ital' axis on the STAT table:
    ttFont = TTFont(TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"))
    assert_results_contain(check(ttFont), FAIL, "invalid-name")

    # LibreCaslonText is good though:
    ttFont = TTFont(TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf"))
    assert_PASS(check(ttFont))

    # Let's break it by setting an invalid coordinate for "Bold":
    assert (
        ttFont["STAT"].table.AxisValueArray.AxisValue[3].ValueNameID
        == ttFont["name"].names[4].nameID
    )
    assert ttFont["name"].names[4].toUnicode() == "Bold"
    # instead of the expected 700
    # Note: I know it is AxisValue[3] and names[4]
    # because I inspected the font using ttx.
    ttFont["STAT"].table.AxisValueArray.AxisValue[3].Value = 800
    assert_results_contain(check(ttFont), FAIL, "bad-coordinate")

    # Let's remove all Axis Values. This will fail since we Google Fonts
    # requires them.
    ttFont["STAT"].table.AxisValueArray = None
    assert_results_contain(check(ttFont), FAIL, "missing-axis-values")


def test_check_metadata_consistent_axis_enumeration():
    """Validate VF axes match the ones declared on METADATA.pb."""
    check = CheckTester(
        "com.google.fonts/check/metadata/consistent_axis_enumeration",
    )

    # The axis tags of CabinVF,
    # are properly declared on its METADATA.pb:
    font = TEST_FILE("cabinvf/Cabin[wdth,wght].ttf")
    assert_PASS(check(font))

    md = Font(font).family_metadata
    md.axes[
        1
    ].tag = (
        "wdth"  # this effectively removes the "wght" axis while not adding an extra one
    )
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "missing-axes"
    )

    md.axes[1].tag = "ouch"  # and this is an unwanted extra axis
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "extra-axes"
    )


def test_check_STAT_axis_order():
    """Check axis ordering on the STAT table."""
    check = CheckTester("com.google.fonts/check/STAT/axis_order")

    fonts = [TEST_FILE("cabinvf/Cabin[wdth,wght].ttf")]
    assert_results_contain(check(fonts), INFO, "summary")

    fonts = [TEST_FILE("merriweather/Merriweather-Regular.ttf")]
    assert_results_contain(check(fonts), SKIP, "missing-STAT")

    # A real-world case here would be a corrupted TTF file.
    # This clearly is not a TTF, but is good enough for testing:
    fonts = [TEST_FILE("merriweather/METADATA.pb")]
    assert_results_contain(check(fonts), INFO, "bad-font")


def test_check_metadata_escaped_strings():
    """Ensure METADATA.pb does not use escaped strings."""
    check = CheckTester("com.google.fonts/check/metadata/escaped_strings")

    good = TEST_FILE("issue_2932/good/SomeFont-Regular.ttf")
    assert_PASS(check(good))

    bad = TEST_FILE("issue_2932/bad/SomeFont-Regular.ttf")
    assert_results_contain(check(bad), FAIL, "escaped-strings")


def test_check_metadata_designer_profiles():
    """METADATA.pb: Designer is listed with the correct name on
    the Google Fonts catalog of designers?"""
    check = CheckTester("com.google.fonts/check/metadata/designer_profiles")

    # Delve Withrington is still not listed on the designers catalog.
    # Note: Once it is listed, this code-test will start failing
    # and will need to be updated.
    font = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_results_contain(check(font), WARN, "profile-not-found")

    # Cousine lists designers: "Multiple Designers"
    font = TEST_FILE("cousine/Cousine-Regular.ttf")
    assert_results_contain(check(font), FAIL, "multiple-designers")

    # This reference Merriweather font family lists "Sorkin Type" in its METADATA.pb
    # file. And this foundry has a good profile on the catalog.
    font = TEST_FILE("merriweather/Merriweather-Regular.ttf")
    assert_PASS(check(font))

    # TODO: FAIL, "mismatch"
    # TODO: FAIL, "link-field"
    # TODO: FAIL, "missing-avatar"
    # TODO: FAIL, "bad-avatar-filename"


def test_check_mandatory_avar_table():
    """Ensure variable fonts include an avar table."""
    check = CheckTester("com.google.fonts/check/mandatory_avar_table")

    ttFont = TTFont(TEST_FILE("ibmplexsans-vf/IBMPlexSansVar-Roman.ttf"))
    assert_PASS(check(ttFont))

    del ttFont["avar"]
    assert_results_contain(check(ttFont), WARN, "missing-avar")


def test_check_description_family_update():
    """
    On a family update, the DESCRIPTION.en_us.html file should ideally also be updated.
    """
    check = CheckTester("com.google.fonts/check/description/family_update")

    font = TEST_FILE("abeezee/ABeeZee-Regular.ttf")
    ABEEZEE_DESC = (
        "https://raw.githubusercontent.com/google/fonts/"
        "main/ofl/abeezee/DESCRIPTION.en_us.html"
    )
    import requests

    desc = requests.get(ABEEZEE_DESC, timeout=10).text
    assert_results_contain(
        check(MockFont(file=font, description=desc)), WARN, "description-not-updated"
    )

    assert_PASS(check(MockFont(file=font, description=desc + "\nSomething else...")))


def test_check_os2_use_typo_metrics():
    """All non-CJK fonts checked with the googlefonts profile
    should have OS/2.fsSelection bit 7 (USE TYPO METRICS) set."""
    check = CheckTester("com.google.fonts/check/os2/use_typo_metrics")

    ttFont = TTFont(TEST_FILE("abeezee/ABeeZee-Regular.ttf"))
    fsel = ttFont["OS/2"].fsSelection

    # set bit 7
    ttFont["OS/2"].fsSelection = fsel | (1 << 7)
    assert_PASS(check(ttFont))

    # clear bit 7
    ttFont["OS/2"].fsSelection = fsel & ~(1 << 7)
    assert_results_contain(check(ttFont), FAIL, "missing-os2-fsselection-bit7")


# TODO: If I recall correctly, there was something wrong with
#       code-tests that try to ensure a check skips.
#       I will have to review this one at some point to verify
#       if that's the reason for this test not working properly.
#
#              -- Felipe Sanches (May 31, 2021)
def TODO_test_check_os2_use_typo_metrics_with_cjk():
    """All CJK fonts checked with the googlefonts profile should skip this check"""
    check = CheckTester("com.google.fonts/check/os2/use_typo_metrics")

    tt_pass_clear = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))
    tt_pass_set = TTFont(TEST_FILE("cjk/SourceHanSans-Regular.otf"))

    fs_selection = 0

    # test skip with font that contains cleared bit
    tt_pass_clear["OS/2"].fsSelection = fs_selection
    # test skip with font that contains set bit
    tt_pass_set["OS/2"].fsSelection = fs_selection | (1 << 7)

    assert_SKIP(
        check(
            MockFont(
                file=TEST_FILE("cjk/SourceHanSans-Regular.otf"), ttFont=tt_pass_clear
            )
        )
    )
    assert_SKIP(check(tt_pass_set))


def test_check_missing_small_caps_glyphs():
    """Check small caps glyphs are available."""
    # check = CheckTester("com.google.fonts/check/missing_small_caps_glyphs")
    # TODO: Implement-me!


def test_check_stylisticset_description():
    """Ensure Stylistic Sets have description."""
    # check = CheckTester("com.google.fonts/check/stylisticset_description")
    # TODO: Implement-me!


def test_check_meta_script_lang_tags():
    """Ensure font has ScriptLangTags in the 'meta' table."""
    check = CheckTester("com.google.fonts/check/meta/script_lang_tags")

    # This sample font from the Noto project declares
    # the script/lang tags in the meta table correctly:
    ttFont = TTFont(TEST_FILE("meta_tag/NotoSansPhagsPa-Regular-with-meta.ttf"))
    assert_results_contain(check(ttFont), INFO, "dlng-tag")
    assert_results_contain(check(ttFont), INFO, "slng-tag")

    del ttFont["meta"].data["dlng"]
    assert_results_contain(check(ttFont), FAIL, "missing-dlng-tag")

    del ttFont["meta"].data["slng"]
    assert_results_contain(check(ttFont), FAIL, "missing-slng-tag")

    del ttFont["meta"]
    assert_results_contain(check(ttFont), WARN, "lacks-meta-table")


def test_check_no_debugging_tables():
    """Ensure fonts do not contain any preproduction tables."""
    check = CheckTester("com.google.fonts/check/no_debugging_tables")

    ttFont = TTFont(TEST_FILE("overpassmono/OverpassMono-Regular.ttf"))
    assert_results_contain(check(ttFont), WARN, "has-debugging-tables")

    del ttFont["FFTM"]
    assert_PASS(check(ttFont))


def test_check_metadata_family_directory_name():
    """Check family directory name."""
    check = CheckTester("com.google.fonts/check/metadata/family_directory_name")

    font = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_PASS(check(font))
    old_md = Font(font).family_metadata

    # Note:
    # Here I explicitly pass 'family_metadata' to avoid it being recomputed
    # after I make the family_directory wrong:
    assert_results_contain(
        check(MockFont(file=font, family_metadata=old_md, family_directory="overpass")),
        FAIL,
        "bad-directory-name",
    )


def test_can_shape():
    font = TTFont(
        portable_path("data/test/source-sans-pro/OTF/SourceSansPro-Regular.otf")
    )
    assert can_shape(font, "ABC")
    assert not can_shape(font, "こんにちは")


def test_check_render_own_name():
    """Check family directory name."""
    check = CheckTester("com.google.fonts/check/render_own_name")

    ttFont = TEST_FILE("overpassmono/OverpassMono-Regular.ttf")
    assert_PASS(check(ttFont))

    ttFont = TEST_FILE("noto_sans_tamil_supplement/NotoSansTamilSupplement-Regular.ttf")
    assert_results_contain(check(ttFont), FAIL, "render-own-name")


def test_check_repo_sample_image():
    """Check README.md has a sample image."""
    check = CheckTester("com.google.fonts/check/repo/sample_image")

    # That's what we'd like to see:
    # README.md including a sample image and highlighting it in the
    # upper portion of the document (no more than 10 lines from the top).
    readme = TEST_FILE("issue_2898/good/README.md")
    assert_PASS(check(readme))

    # This one is still good, but places the sample image too late in the page:
    readme = TEST_FILE("issue_2898/not-ideal-placement/README.md")
    assert_results_contain(check(readme), WARN, "not-ideal-placement")

    # Here's a README.md in a project completely lacking such sample image.
    # This will likely become a FAIL in the future:
    readme = TEST_FILE("issue_2898/no-sample/README.md")
    assert_results_contain(check(readme), WARN, "no-sample")  # FIXME: Make this a FAIL!

    # This is really broken, as it references an image that is not available:
    readme = TEST_FILE("issue_2898/image-missing/README.md")
    assert_results_contain(check(readme), FAIL, "image-missing")

    # An here a README.md that does not include any sample image,
    # while an image file can be found within the project's directory tree.
    # This image could potentially be a font sample, so we let the user know
    # that it might be the case:
    readme = TEST_FILE("issue_2898/image-not-displayed/README.md")
    assert_results_contain(check(readme), WARN, "image-not-displayed")


def test_check_metadata_can_render_samples():
    """Check README.md has a sample image."""
    check = CheckTester("com.google.fonts/check/metadata/can_render_samples")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font))

    # This will try to render using strings provided by the gflanguages package
    # Available at https://pypi.org/project/gflanguages/
    md = Font(font).family_metadata
    md.languages.append("non_Runr")  # Cabin does not support Old Nordic Runic
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "sample-text"
    )

    # TODO: expand the check to also validate rendering of
    #       text provided explicitely on the sample_text field of METADATA.pb


def test_check_description_urls():
    """URLs on DESCRIPTION file must not display http(s) prefix."""
    check = CheckTester("com.google.fonts/check/description/urls")

    font = TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf")
    assert_PASS(check(font))

    font = TEST_FILE("cabinvfbeta/CabinVFBeta.ttf")
    assert_results_contain(check(font), FAIL, "prefix-found")

    good_desc = Font(font).description.replace(">https://", ">")
    assert_PASS(check(MockFont(file=font, description=good_desc)))

    bad_desc = good_desc.replace(">github.com/impallari/Cabin<", "><")
    assert_results_contain(
        check(MockFont(file=font, description=bad_desc)), FAIL, "empty-link-text"
    )


def test_check_metadata_unsupported_subsets():
    """Check for METADATA subsets with zero support."""
    check = CheckTester("com.google.fonts/check/metadata/unsupported_subsets")

    font = TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf")
    assert_PASS(check(font))

    md = Font(font).family_metadata
    md.subsets.extend(["foo"])
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "unknown-subset"
    )

    del md.subsets[:]
    md.subsets.extend(["cyrillic"])
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)), FAIL, "unsupported-subset"
    )


def test_check_metadata_category_hints():
    """
    Check if category on METADATA.pb matches what can be inferred from the family name.
    """
    check = CheckTester("com.google.fonts/check/metadata/category_hints")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_PASS(check(font), "with a familyname without any of the keyword hints...")

    md = Font(font).family_metadata
    md.name = "Seaweed Script"
    md.category[:] = ["DISPLAY"]
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        WARN,
        "inferred-category",
        f'with a bad category "{md.category}" for familyname "{md.name}"...',
    )

    md.name = "Red Hat Display"
    md.category[:] = ["SANS_SERIF"]
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        WARN,
        "inferred-category",
        f'with a bad category "{md.category}" for familyname "{md.name}"...',
    )

    md.name = "Seaweed Script"
    md.category[:] = ["HANDWRITING"]
    assert_PASS(
        check(MockFont(file=font, family_metadata=md)),
        f'with a good category "{md.category}" for familyname "{md.name}"...',
    )

    md.name = "Red Hat Display"
    md.category[:] = ["DISPLAY"]
    assert_PASS(
        check(MockFont(file=font, family_metadata=md)),
        f'with a good category "{md.category}" for familyname "{md.name}"...',
    )


@pytest.mark.parametrize(
    """fp,mod,result""",
    [
        # font includes condensed fvar instances so it should fail
        (TEST_FILE("cabinvfbeta/CabinVFBeta.ttf"), [], FAIL),
        # official fonts have been fixed so this should pass
        (TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"), [], PASS),
        (TEST_FILE("cabinvf/Cabin-Italic[wdth,wght].ttf"), [], PASS),
        # lets inject an instance which is not a multiple of 100
        (TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"), [("Book", 450)], FAIL),
    ],
)
def test_check_fvar_instances(fp, mod, result):
    """Check font fvar instances are correct"""
    from fontTools.ttLib.tables._f_v_a_r import NamedInstance

    check = CheckTester("com.google.fonts/check/fvar_instances")
    ttFont = TTFont(fp)
    expected = expected_font_names(ttFont, [])
    if mod:
        for name, wght_val in mod:
            inst = NamedInstance()
            inst.subfamilyNameID = ttFont["name"].addName(name)
            inst.coordinates = {"wght": wght_val}
            ttFont["fvar"].instances.append(inst)

    if result == PASS:
        assert_PASS(check(ttFont), "with a good font")
    elif result == FAIL:
        assert_results_contain(
            check(ttFont),
            FAIL,
            "bad-fvar-instances",
            "with a bad font",
        )


@pytest.mark.parametrize(
    """fps,new_stat,result""",
    [
        # Fail (we didn't really know what we were doing at this stage)
        (
            [
                TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"),
                TEST_FILE("cabinvf/Cabin-Italic[wdth,wght].ttf"),
            ],
            [],
            FAIL,
        ),
        # Fix previous test for Cabin[wdth,wght].ttf
        (
            [
                TEST_FILE("cabinvf/Cabin[wdth,wght].ttf"),
                TEST_FILE("cabinvf/Cabin-Italic[wdth,wght].ttf"),
            ],
            # STAT for Cabin[wdth,wght].ttf
            [
                {
                    "name": "Weight",
                    "tag": "wght",
                    "values": [
                        {
                            "value": 400,
                            "name": "Regular",
                            "linkedValue": 700.0,
                            "flags": 0x2,
                        },
                        {"value": 500, "name": "Medium"},
                        {"value": 600, "name": "SemiBold"},
                        {"value": 700, "name": "Bold"},
                    ],
                },
                {
                    "name": "Width",
                    "tag": "wdth",
                    "values": [
                        {"value": 75, "name": "Condensed"},
                        {"value": 87.5, "name": "SemiCondensed"},
                        {"value": 100, "name": "Normal", "flags": 0x2},
                    ],
                },
                {
                    "name": "Italic",
                    "tag": "ital",
                    "values": [
                        {
                            "value": 0.0,
                            "name": "Normal",
                            "linkedValue": 1.0,
                            "flags": 0x2,
                        }
                    ],
                },
            ],
            PASS,
        ),
    ],
)
def test_check_STAT(fps, new_stat, result):
    """Check STAT table Axis Values are correct"""
    # more comprehensive checks are available in the axisregistry:
    # https://github.com/googlefonts/axisregistry/blob/main/tests/test_names.py#L442
    # this check merely exists to check that everything is hooked up correctly
    from fontTools.otlLib.builder import buildStatTable

    check = CheckTester("com.google.fonts/check/STAT")
    ttFonts = [TTFont(f) for f in fps]
    ttFont = ttFonts[0]
    expected = expected_font_names(ttFont, ttFonts)
    if new_stat:
        buildStatTable(ttFont, new_stat)

    if result == PASS:
        assert_PASS(
            check(MockFont(file=fps[0], ttFont=ttFont, expected_font_names=expected)),
            "with a good font",
        )
    elif result == FAIL:
        assert_results_contain(
            check(MockFont(file=fps[0], ttFont=ttFont, expected_font_names=expected)),
            FAIL,
            "bad-axis-values",
            "with a bad font",
        )


def test_check_colorfont_tables():
    """Check font has the expected color font tables."""
    from fontTools.ttLib import newTable

    check = CheckTester("com.google.fonts/check/colorfont_tables")

    ttFont = TTFont(TEST_FILE("color_fonts/noto-glyf_colr_1.ttf"))
    assert "SVG " not in ttFont.keys()
    assert "COLR" in ttFont.keys()
    assert ttFont["COLR"].version == 1
    # Check colr v1 static font has an svg table (since v1 isn't yet broadly supported).
    # Will fail since font doesn't have one.
    assert_results_contain(
        check(ttFont), FAIL, "add-svg", "with a static colr v1 font lacking SVG table"
    )

    # Fake a variable font by adding an fvar table.
    ttFont["fvar"] = newTable("fvar")
    assert "fvar" in ttFont.keys()

    # SVG does not support OpenType Variations
    assert_PASS(check(ttFont), "with a variable color font without SVG table")

    # Fake an SVG table:
    ttFont["SVG "] = newTable("SVG ")
    assert "SVG " in ttFont.keys()

    assert_results_contain(
        check(ttFont), FAIL, "variable-svg", "with a variable color font with SVG table"
    )

    # Make it a static again:
    del ttFont["fvar"]
    assert "fvar" not in ttFont.keys()

    assert "SVG " in ttFont.keys()
    assert "COLR" in ttFont.keys()
    assert ttFont["COLR"].version == 1
    assert_PASS(check(ttFont), "with a static colr v1 font containing both tables.")

    # Now downgrade to colr table to v0:
    ttFont["COLR"].version = 0
    assert "SVG " in ttFont.keys()
    assert_results_contain(
        check(ttFont),
        FAIL,
        "drop-svg",
        "with a font which should not have an SVG table",
    )

    # Delete colr table and keep SVG:
    del ttFont["COLR"]
    assert "SVG " in ttFont.keys()
    assert "COLR" not in ttFont.keys()
    assert_results_contain(
        check(ttFont), FAIL, "add-colr", "with a font which should have a COLR table"
    )

    # Finally delete both color font tables
    del ttFont["SVG "]
    assert "SVG " not in ttFont.keys()
    assert "COLR" not in ttFont.keys()
    assert_PASS(check(ttFont), "with a good font without SVG or COLR tables.")


def test_check_color_cpal_brightness():
    """Color layers should have a minimum brightness"""
    check = CheckTester("com.google.fonts/check/color_cpal_brightness")

    font = TEST_FILE("color_fonts/AmiriQuranColored_too_dark.ttf")
    assert_results_contain(
        check(font),
        WARN,
        "glyphs-too-dark-or-too-bright",
        "with a colrv0 font with doo dark layers",
    )

    font = TEST_FILE("color_fonts/AmiriQuranColored.ttf")
    assert_PASS(check(font), "with a colrv0 font with good layer colors")


def test_check_empty_glyph_on_gid1_for_colrv0():
    """Put an empty glyph on GID 1 right after the .notdef glyph for COLRv0 fonts."""

    def gid1area(ttFont):
        from fontTools.pens.areaPen import AreaPen

        glyphOrder = ttFont.getGlyphOrder()
        glyphSet = ttFont.getGlyphSet()
        pen = AreaPen(glyphSet)
        gid1 = glyphSet[glyphOrder[1]]
        gid1.draw(pen)
        return pen.value

    check = CheckTester("com.google.fonts/check/empty_glyph_on_gid1_for_colrv0")

    ttFont = TTFont(TEST_FILE("color_fonts/AmiriQuranColored_gid1_notempty.ttf"))
    assert (
        "COLR" in ttFont.keys()
        and ttFont["COLR"].version == 0
        and gid1area(ttFont) != 0
    )
    assert_results_contain(
        check(ttFont),
        FAIL,
        "gid1-has-contours",
        "with a font with COLR table but no empty glyph on GID 1.",
    )

    ttFont = TTFont(TEST_FILE("color_fonts/AmiriQuranColored.ttf"))
    assert (
        "COLR" in ttFont.keys()
        and ttFont["COLR"].version == 0
        and gid1area(ttFont) == 0
    )
    assert_PASS(
        check(ttFont), "with a good font with COLR table and an empty glyph on GID 1."
    )


def test_check_has_article():
    """Noto fonts must have an ARTICLE.en_us.html file, others with an
    article should have an empty DESCRIPTION"""
    check = CheckTester("com.google.fonts/check/description/has_article")

    font = TEST_FILE("notosanskhudawadi/NotoSansKhudawadi-Regular.ttf")
    assert_PASS(check(font), "with a good font")

    font = TEST_FILE("noto_sans_tamil_supplement/NotoSansTamilSupplement-Regular.ttf")
    assert_results_contain(check(font), FAIL, "missing-article", "with a bad font")

    font = TEST_FILE("tirodevanagarihindi/TiroDevanagariHindi-Regular.ttf")
    assert_results_contain(
        check(font),
        FAIL,
        "description-and-article",
        "with a font with description and article",
    )


def test_check_description_has_unsupported_elements():
    """Check the description doesn't contain unsupported html elements"""
    check = CheckTester(
        "com.google.fonts/check/description/has_unsupported_elements",
    )
    font = TEST_FILE("librecaslontext/LibreCaslonText[wght].ttf")
    assert_PASS(check(font))

    font = TEST_FILE("unsupported_html_elements/ABeeZee-Regular.ttf")
    assert_results_contain(
        check(font), FATAL, "unsupported-elements", "with a bad font"
    )


def test_check_italic_axis_in_stat_is_boolean():
    """Ensure 'ital' STAT axis is boolean value"""
    check = CheckTester(
        "com.google.fonts/check/italic_axis_in_stat_is_boolean",
        profile=googlefonts_profile,
    )

    # PASS
    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    assert_PASS(check(TTFont(font)))

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    assert_PASS(check(TTFont(font)))

    # FAIL
    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Value = 1
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-value")

    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Flags = 0
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-flag")

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Value = 0
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-value")

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].Flags = 2
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-flag")

    font = TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    ttFont["STAT"].table.AxisValueArray.AxisValue[6].LinkedValue = None
    assert_results_contain(check(ttFont), FAIL, "wrong-ital-axis-linkedvalue")


def test_check_italic_axis_last():
    """Ensure 'ital' STAT axis is boolean value"""
    check = CheckTester(
        "com.google.fonts/check/italic_axis_last",
        profile=googlefonts_profile,
    )

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    ttFont = TTFont(font)
    # Move last axis (ital) to the front
    ttFont["STAT"].table.DesignAxisRecord.Axis = [
        ttFont["STAT"].table.DesignAxisRecord.Axis[-1]
    ] + ttFont["STAT"].table.DesignAxisRecord.Axis[:-1]
    assert_results_contain(check(ttFont), FAIL, "ital-axis-not-last")

    font = TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf")
    assert_PASS(check(font))


def test_check_metadata_unreachable_subsetting():
    """Check for codepoints not covered by METADATA subsetting"""
    check = CheckTester("com.google.fonts/check/metadata/unreachable_subsetting")

    font = TEST_FILE("notosanskhudawadi/NotoSansKhudawadi-Regular.ttf")
    assert_PASS(check(font), "with a good font")

    font = TEST_FILE("cabin/Cabin-Regular.ttf")
    assert_results_contain(
        check(font), WARN, "unreachable-subsetting", "with a bad font"
    )

    font = TEST_FILE("playfair/Playfair-Italic[opsz,wdth,wght].ttf")
    assert_results_contain(
        check(font),
        WARN,
        "unreachable-subsetting",
        "with a bad font and no METADATA.pb",
    )


def test_check_alt_caron():
    """Check accent of Lcaron, dcaron, lcaron, tcaron"""
    check = CheckTester(
        "com.google.fonts/check/alt_caron",
        profile=googlefonts_profile,
    )

    ttFont = TTFont(TEST_FILE("annie/AnnieUseYourTelescope-Regular.ttf"))
    assert_results_contain(
        check(ttFont), FAIL, "bad-mark"  # deviation from universal profile
    )

    assert_results_contain(check(ttFont), FAIL, "wrong-mark")

    ttFont = TTFont(TEST_FILE("cousine/Cousine-Bold.ttf"))
    assert_results_contain(check(ttFont), WARN, "decomposed-outline")

    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))
    assert_PASS(check(ttFont))


def test_check_shape_languages():
    """Shapes languages in all GF glyphsets."""
    check = CheckTester("com.google.fonts/check/glyphsets/shape_languages")

    test_font = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_PASS(check(test_font))

    test_font = TTFont(TEST_FILE("BadGrades/BadGrades-VF.ttf"))
    assert_results_contain(check(test_font), FAIL, "no-glyphset-supported")

    test_font = TTFont(TEST_FILE("annie/AnnieUseYourTelescope-Regular.ttf"))
    assert_results_contain(check(test_font), FAIL, "failed-language-shaping")


def test_check_varfont_bold_wght_coord():
    """The variable font 'wght' (Weight) axis coordinate
    must be 700 on the 'Bold' instance."""
    check = CheckTester("com.google.fonts/check/varfont/bold_wght_coord")

    # Our reference varfont CabinVFBeta.ttf
    # has a good Bold:wght coordinate
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    assert_PASS(check(ttFont), "with a good Bold:wght coordinate...")

    # We then change the value to ensure the problem is properly detected by the check:
    ttFont["fvar"].instances[3].coordinates["wght"] = 600
    assert_results_contain(
        check(ttFont), FAIL, "wght-not-700", "with a bad Bold:wght coordinage (600)..."
    )

    # Check we skip when we don't have a 700 weight.
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    del ttFont["fvar"].instances[3]
    ttFont["fvar"].axes[0].maxValue = 600
    assert_results_contain(check(ttFont), SKIP, "no-bold-weight")


def test_check_metadata_has_tags():
    """The font has tags in the GF Tags spreadsheet"""
    check = CheckTester("com.google.fonts/check/metadata/has_tags")

    font = "data/test/merriweather/Merriweather-Regular.ttf"
    assert_PASS(check(font), "with a name that's in the spreadsheet...")

    md = Font(font).family_metadata
    md.name = "Not Merriweather"
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FATAL,
        "no-tags",
        "with a name that doesn't appear...",
    )


def test_check_metadata_minisite_url():
    """Validate minisite_url field"""
    check = CheckTester("com.google.fonts/check/metadata/minisite_url")

    font = "data/test/merriweather/Merriweather-Regular.ttf"
    assert_results_contain(check(font), INFO, "lacks-minisite-url")

    md = Font(font).family_metadata
    md.minisite_url = "a_good_one.com"
    assert_PASS(check(MockFont(file=font, family_metadata=md)), "with a good one")

    md.minisite_url = "some_url/"
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "trailing-clutter",
        "with a minisite_url with unnecessary trailing forward-slash",
    )

    md.minisite_url = "some_url/index.htm"
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "trailing-clutter",
        "with a minisite_url with unnecessary trailing /index.htm",
    )

    md.minisite_url = "some_url/index.html"
    assert_results_contain(
        check(MockFont(file=font, family_metadata=md)),
        FAIL,
        "trailing-clutter",
        "with a minisite_url with unnecessary trailing /index.html",
    )


def test_check_linegaps():
    """Checking Vertical Metric Linegaps."""
    check = CheckTester("com.google.fonts/check/linegaps", profile=googlefonts_profile)

    # Our reference Mada Regular is know to be bad here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

    # But just to be sure, we first explicitely set
    # the values we're checking for:
    ttFont["hhea"].lineGap = 1
    ttFont["OS/2"].sTypoLineGap = 0
    assert_results_contain(check(ttFont), FAIL, "hhea", "with non-zero hhea.lineGap...")

    # Then we run the check with a non-zero OS/2.sTypoLineGap:
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 1
    assert_results_contain(
        check(ttFont), FAIL, "OS/2", "with non-zero OS/2.sTypoLineGap..."
    )

    # And finaly we fix it by making both values equal to zero:
    ttFont["hhea"].lineGap = 0
    ttFont["OS/2"].sTypoLineGap = 0
    assert_PASS(check(ttFont))

    # Confirm the check yields FAIL if the font doesn't have a required table
    del ttFont["OS/2"]
    assert_results_contain(check(ttFont), FAIL, "lacks-table")


def test_check_article_images():
    """Validate location, size and resolution of article images."""
    check = CheckTester("com.google.fonts/check/article/images")

    # This one is know to be bad:
    family_dir = TEST_FILE("tirodevanagarihindi")

    assert_results_contain(
        check(MockFont(family_directory=family_dir)),
        WARN,
        "misplaced-image-files",
        "The files are not in the correct directory...",
    )

    # TODO: test WARN "lacks-article"
    # TODO: test FAIL "image-too-large"
    # TODO: test PASS


def test_varfont_instances_in_order():
    ttFont = TTFont("data/test/cabinvfbeta/CabinVFBeta.ttf")
    check = CheckTester("com.google.fonts/check/varfont/instances_in_order")
    assert_PASS(check(ttFont))

    # Move the second instance to the front
    ttFont["fvar"].instances = [
        ttFont["fvar"].instances[1],
        ttFont["fvar"].instances[0],
    ] + ttFont["fvar"].instances[1:]
    assert_results_contain(check(ttFont), FAIL, "instances-not-in-order")
