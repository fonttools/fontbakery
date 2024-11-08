import pytest
from fontTools.ttLib import TTFont

from conftest import check_id
from fontbakery.codetesting import (
    assert_PASS,
    assert_SKIP,
    assert_results_contain,
    GLYPHSAPP_TEST_FILE,
    TEST_FILE,
)
from fontbakery.constants import NameID
from fontbakery.status import FAIL, WARN


@pytest.fixture
def test_ttFont():
    return TTFont(TEST_FILE("selawik/Selawik-fvar-test-VTT.ttf"), lazy=True)


@check_id("name_id_1")
def test_check_name_id_1(check, test_ttFont):
    """Font has a name with ID 1."""

    assert_PASS(check(test_ttFont), "with a good font...")

    # TODO: test a FAIL case


@check_id("name_id_2")
def test_check_name_id_2(check, test_ttFont):
    """Font has a name with ID 2."""

    assert_PASS(check(test_ttFont), "with a good font...")

    # TODO: test a FAIL case


@check_id("name_length_req")
def test_check_name_length_req(check, test_ttFont):
    """Maximum allowed length for family and subfamily names."""

    assert_PASS(check(test_ttFont), "with a good font...")

    # TODO: test a FAIL case


@check_id("typographic_family_name")
def test_check_typographic_family_name(check, test_ttFont):
    """Typographic Family name consistency."""

    family = [
        test_ttFont,  # FIXME: This must be tested with more than a single font file!
    ]
    assert_PASS(check(family), "with a good family...")

    # TODO: test a FAIL case


@check_id("name/char_restrictions")
def test_check_name_char_restrictions(check):
    """Are there disallowed characters in the restricted NAME table entries?"""

    # Our reference Merriweather Regular is known to be good
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # So it must PASS the check:
    assert_PASS(check(ttFont), "with a good font...")

    #  The OpenType spec requires a subset of ASCII
    #  (any printable characters except "[]{}()<>/%") for
    #  POSTSCRIPT_NAME (nameID 6),
    #  POSTSCRIPT_CID_NAME (nameID 20), and
    #  an even smaller subset ("a-zA-Z0-9") for
    #  VARIATIONS_POSTSCRIPT_NAME_PREFIX (nameID 25).

    # Choose an arbitrary name entry to mess up with:
    index = 5

    # And check detection on nameId 6:
    ttFont["name"].names[index].nameID = NameID.POSTSCRIPT_NAME
    ttFont["name"].names[index].string = "ILike{Braces}!".encode(encoding="utf_16_be")

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-string",
        "with disallowed characters on nameID 6 entry (Postscript name)...",
    )

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-strings",
        "with disallowed characters on nameID 6 entry (Postscript name)...",
    )

    # Then reload the good font
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # And check detection of a problem on nameId 20:
    ttFont["name"].names[index].nameID = NameID.POSTSCRIPT_CID_NAME
    ttFont["name"].names[index].string = "Infração".encode(encoding="utf_16_be")

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-string",
        "with disallowed characters on nameID 20 entry (Postscript CID findfont name)...",
    )

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-strings",
        "with disallowed characters on nameID 20 entry (Postscript CID findfont name)...",
    )

    # Then reload the good font again
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # And check detection of a problem on nameId 25.
    # In this case the exclamation mark alone should be sufficient to trigger the error:
    ttFont["name"].names[index].nameID = NameID.VARIATIONS_POSTSCRIPT_NAME_PREFIX
    ttFont["name"].names[index].string = "ILikeSimpleStuff!".encode(
        encoding="utf_16_be"
    )
    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-string",
        "with disallowed characters on nameID 25 entry (Variations Postscript name prefix)...",
    )

    assert_results_contain(
        check(ttFont),
        FAIL,
        "bad-strings",
        "with disallowed characters on nameID 25 entry (Variations Postscript name prefix)...",
    )

    # Reload the good font once more:
    ttFont = TTFont(TEST_FILE("merriweather/Merriweather-Regular.ttf"))

    # Let's check a good case of a non-ascii on the name table then!
    ttFont["name"].names[index].nameID = 19
    ttFont["name"].names[index].string = "[{<(Fantástico! /%)>}]".encode(
        encoding="utf_16_be"
    )
    assert_PASS(
        check(ttFont),
        "with various characters on entries with unrestricted nameId...",
    )


@check_id("name/family_and_style_max_length")
def test_check_name_family_and_style_max_length(check):
    """Name table entries should not be too long."""

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


@check_id("glyphs_file/name/family_and_style_max_length")
def DISABLED_test_check_glyphs_file_name_family_and_style_max_length(check):
    """Combined length of family and style must not exceed 27 characters."""

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


@check_id("no_mac_entries")
def test_check_name_no_mac_entries(check):
    """Ensure font doesn't have Mac name table entries (platform=1)."""

    font = TEST_FILE("abeezee/ABeeZee-Italic.ttf")
    assert_results_contain(
        check(font), FAIL, "mac-names", "with a font containing Mac names"
    )

    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    assert_PASS(check(font), "with a font without Mac names")


@check_id("name/no_copyright_on_description")
def test_check_name_no_copyright_on_description(check):
    """Description strings in the name table must not contain copyright info."""

    # Our reference Mada Regular is know to be good here.
    ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))
    assert_PASS(check(ttFont), "with a good font...")

    # here we add a "Copyright" string to a NameID.DESCRIPTION
    for i, name in enumerate(ttFont["name"].names):
        if name.nameID == NameID.DESCRIPTION:
            ttFont["name"].names[i].string = "Copyright".encode(name.getEncoding())

    assert_results_contain(
        check(ttFont), FAIL, "copyright-on-description", "with a bad font..."
    )


@check_id("name/italic_names")
def test_check_italic_names(check):
    def get_name(font, nameID):
        for entry in font["name"].names:
            if entry.nameID == nameID:
                return entry.toUnicode()

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

    # Fonts without Name ID 16 & 17

    # PASS or SKIP
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Regular.ttf"))
    assert_SKIP(check(ttFont))

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Italic.ttf"))
    assert_PASS(check(ttFont))

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Medium.ttf"))
    assert_SKIP(check(ttFont))

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Bold.ttf"))
    assert_SKIP(check(ttFont))

    ttFont = TTFont(TEST_FILE("cabin/Cabin-BoldItalic.ttf"))
    assert_PASS(check(ttFont))

    # FAIL
    ttFont = TTFont(TEST_FILE("cabin/Cabin-Italic.ttf"))
    set_name(ttFont, 1, get_name(ttFont, 1) + " Italic")
    assert_results_contain(check(ttFont), FAIL, "bad-familyname")

    ttFont = TTFont(TEST_FILE("cabin/Cabin-Italic.ttf"))
    set_name(ttFont, 2, "Regular")
    assert_results_contain(check(ttFont), FAIL, "bad-subfamilyname")

    # This file is faulty as-is
    ttFont = TTFont(TEST_FILE("cabin/Cabin-MediumItalic.ttf"))
    assert_results_contain(check(ttFont), FAIL, "bad-subfamilyname")
    # Fix it
    set_name(ttFont, 1, "Cabin Medium")
    set_name(ttFont, 2, "Italic")
    assert_PASS(check(ttFont))

    # Fonts with Name ID 16 & 17

    # PASS or SKIP
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans[BNCE,INFM,SPAC,wght].ttf"))
    assert_SKIP(check(ttFont))

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    assert_PASS(check(ttFont))

    # FAIL
    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    set_name(ttFont, 16, "Shantell Sans Italic")
    assert_results_contain(check(ttFont), FAIL, "bad-typographicfamilyname")

    ttFont = TTFont(TEST_FILE("shantell/ShantellSans-Italic[BNCE,INFM,SPAC,wght].ttf"))
    set_name(ttFont, 17, "Light")
    assert_results_contain(check(ttFont), FAIL, "bad-typographicsubfamilyname")
