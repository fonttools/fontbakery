from fontbakery.prelude import check, disable, Message, PASS, FAIL
from fontbakery.checks.googlefonts.constants import (
    DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    EXPECTED_COPYRIGHT_PATTERN,
)
from fontbakery.constants import NameID


@check(
    id="com.google.fonts/check/metadata/valid_copyright",
    conditions=["font_metadata"],
    rationale="""
        This check aims at ensuring a uniform and legally accurate copyright statement
        on the METADATA.pb copyright entries accross the Google Fonts library.

    """
    + DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal="legacy:check/102",
)
def com_google_fonts_check_metadata_valid_copyright(font_metadata):
    """Copyright notices match canonical pattern in METADATA.pb"""
    import re

    string = font_metadata.copyright.lower()
    if re.search(EXPECTED_COPYRIGHT_PATTERN, string):
        yield PASS, "METADATA.pb copyright string is good"
    else:
        yield FAIL, Message(
            "bad-notice-format",
            f"METADATA.pb: Copyright notices should match a pattern similar to:\n\n"
            f' "Copyright 2020 The Familyname Project Authors (git url)"\n\n'
            f'But instead we have got:\n\n"{string}"',
        )


@check(
    id="com.google.fonts/check/font_copyright",
    rationale="""
        This check aims at ensuring a uniform and legally accurate copyright statement
        on the name table entries of font files accross the Google Fonts library.

    """
    + DESCRIPTION_OF_EXPECTED_COPYRIGHT_STRING_FORMATTING,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal="https://github.com/fonttools/fontbakery/pull/2383",
)
def com_google_fonts_check_font_copyright(ttFont):
    """Copyright notices match canonical pattern in fonts"""
    import re
    from fontbakery.utils import get_name_entry_strings

    passed = True
    for string in get_name_entry_strings(ttFont, NameID.COPYRIGHT_NOTICE):
        if re.search(EXPECTED_COPYRIGHT_PATTERN, string.lower()):
            yield PASS, (
                f"Name Table entry: Copyright field '{string}'"
                f" matches canonical pattern."
            )
        else:
            passed = False
            yield FAIL, Message(
                "bad-notice-format",
                f"Name Table entry: Copyright notices should match"
                f" a pattern similar to:\n\n"
                f'"Copyright 2019 The Familyname Project Authors (git url)"\n\n'
                f'But instead we have got:\n\n"{string}"\n',
            )
    if passed:
        yield PASS, "Name table copyright entries are good"


@disable
@check(id="com.google.fonts/check/glyphs_file/font_copyright")
def com_google_fonts_check_glyphs_file_font_copyright(glyphsFile):
    """Copyright notices match canonical pattern in fonts"""
    import re

    string = glyphsFile.copyright.lower()
    if re.search(EXPECTED_COPYRIGHT_PATTERN, string):
        yield PASS, (
            f"Name Table entry: Copyright field '{string}'"
            f" matches canonical pattern."
        )
    else:
        yield FAIL, Message(
            "bad-notice-format",
            f"Copyright notices should match"
            f' a pattern similar to: "Copyright 2019'
            f' The Familyname Project Authors (git url)"\n'
            f'But instead we have got:\n"{string}"',
        )


@check(
    id="com.google.fonts/check/metadata/copyright_max_length",
    conditions=["font_metadata"],
    proposal="legacy:check/104",
)
def com_google_fonts_check_metadata_copyright_max_length(font_metadata):
    """METADATA.pb: Copyright notice shouldn't exceed 500 chars."""
    if len(font_metadata.copyright) > 500:
        yield FAIL, Message(
            "max-length",
            "METADATA.pb: Copyright notice exceeds"
            " maximum allowed lengh of 500 characteres.",
        )
    else:
        yield PASS, "Copyright notice string is shorter than 500 chars."


@check(
    id="com.google.fonts/check/metadata/nameid/copyright",
    conditions=["font_metadata"],
    proposal="legacy:check/155",
)
def com_google_fonts_check_metadata_nameid_copyright(ttFont, font_metadata):
    """Copyright field for this font on METADATA.pb matches
    all copyright notice entries on the name table ?"""
    passed = True
    for nameRecord in ttFont["name"].names:
        string = nameRecord.string.decode(nameRecord.getEncoding())
        if (
            nameRecord.nameID == NameID.COPYRIGHT_NOTICE
            and string != font_metadata.copyright
        ):
            passed = False
            yield FAIL, Message(
                "mismatch",
                f"Copyright field for this font on METADATA.pb"
                f' ("{font_metadata.copyright}") differs from'
                f" a copyright notice entry on the name table:"
                f' "{string}"',
            )
    if passed:
        yield PASS, (
            "Copyright field for this font on METADATA.pb matches"
            " copyright notice entries on the name table."
        )


@check(
    id="com.google.fonts/check/name/copyright_length",
    rationale="""
        This is an arbitrary max length for the copyright notice field of the name
        table. We simply don't want such notices to be too long. Typically such notices
        are actually much shorter than this with a length of roughly 70 or 80
        characters.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1603",
)
def com_google_fonts_check_name_copyright_length(ttFont):
    """Length of copyright notice must not exceed 500 characters."""
    from fontbakery.utils import get_name_entries

    passed = True
    for notice in get_name_entries(ttFont, NameID.COPYRIGHT_NOTICE):
        notice_str = notice.string.decode(notice.getEncoding())
        if len(notice_str) > 500:
            passed = False
            yield FAIL, Message(
                "too-long",
                f"The length of the following copyright notice"
                f" ({len(notice_str)}) exceeds 500 chars:"
                f' "{notice_str}"',
            )
    if passed:
        yield PASS, (
            "All copyright notice name entries on the"
            " 'name' table are shorter than 500 characters."
        )
