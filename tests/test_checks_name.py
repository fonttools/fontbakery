import pytest
from fontTools.ttLib import TTFont

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    CheckTester,
    GLYPHSAPP_TEST_FILE,
    TEST_FILE,
)
from fontbakery.constants import NameID
from fontbakery.status import FAIL, WARN


@pytest.fixture
def test_ttFont():
    return TTFont(TEST_FILE("selawik/Selawik-fvar-test-VTT.ttf"), lazy=True)


def test_check_name_id_1(test_ttFont):
    """Font has a name with ID 1."""
    check = CheckTester("name_id_1")

    assert_PASS(check(test_ttFont), "with a good font...")

    # TODO: test a FAIL case


def test_check_name_id_2(test_ttFont):
    """Font has a name with ID 2."""
    check = CheckTester("name_id_2")

    assert_PASS(check(test_ttFont), "with a good font...")

    # TODO: test a FAIL case


def test_check_name_length_req(test_ttFont):
    """Maximum allowed length for family and subfamily names."""
    check = CheckTester("name_length_req")

    assert_PASS(check(test_ttFont), "with a good font...")

    # TODO: test a FAIL case


def test_check_typographic_family_name(test_ttFont):
    """Typographic Family name consistency."""
    check = CheckTester("typographic_family_name")

    family = [
        test_ttFont,  # FIXME: This must be tested with more than a single font file!
    ]
    assert_PASS(check(family), "with a good family...")

    # TODO: test a FAIL case


def test_check_name_ascii_only_entries():
    """Are there non-ASCII characters in ASCII-only NAME table entries?"""
    check = CheckTester("name/ascii_only_entries")

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


def test_check_name_family_and_style_max_length():
    """Name table entries should not be too long."""
    check = CheckTester("name/family_and_style_max_length")

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
    check = CheckTester("glyphs_file/name/family_and_style_max_length")

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


def test_check_name_no_mac_entries():
    """Ensure font doesn't have Mac name table entries (platform=1)."""
    check = CheckTester("no_mac_entries")

    font = TEST_FILE("abeezee/ABeeZee-Italic.ttf")
    assert_results_contain(
        check(font), FAIL, "mac-names", "with a font containing Mac names"
    )

    font = TEST_FILE("source-sans-pro/OTF/SourceSansPro-Regular.otf")
    assert_PASS(check(font), "with a font without Mac names")
