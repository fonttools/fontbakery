import re

from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
)
from fontbakery.prelude import check, disable, Message, FAIL, WARN
from fontbakery.utils import get_name_entry_strings


def get_family_name(ttFont):
    """
    Get the family name from the name table.

    TODO: For now, this is just name ID 1. It should be expanded to at least
    check IDs 16 & 21, and ideally do the whole font differentiator heuristic.
    """
    family_name = ttFont["name"].getName(1, 3, 1, 0x0409)
    if family_name is None:
        return None
    return family_name.toUnicode()


def get_subfamily_name(ttFont):
    """
    Get the subfamily name from the name table.

    TODO: For now, this is just name ID 2. It should be expanded to at least
    check IDs 17 & 22, and ideally do the whole font differentiator heuristic.
    """
    subfamily_name = ttFont["name"].getName(2, 3, 1, 0x0409)
    if subfamily_name is None:
        return None
    return subfamily_name.toUnicode()


@check(
    id="name_id_1",
    rationale="""
        Presence of a name ID 1 entry is mandatory.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_id_1(ttFont):
    """Font has a name with ID 1."""
    if not ttFont["name"].getName(1, 3, 1, 0x409):
        yield FAIL, "Font lacks a name with ID 1."


@check(
    id="name_id_2",
    rationale="""
        Presence of a name ID 2 entry is mandatory.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_id_2(ttFont):
    """Font has a name with ID 2."""
    if not ttFont["name"].getName(2, 3, 1, 0x409):
        yield FAIL, "Font lacks a name with ID 2."


@check(
    id="name/ascii_only_entries",
    rationale="""
        The OpenType spec requires ASCII for the POSTSCRIPT_NAME (nameID 6).

        For COPYRIGHT_NOTICE (nameID 0) ASCII is required because that string should be
        the same in CFF fonts which also have this requirement in the OpenType spec.

        Note:
        A common place where we find non-ASCII strings is on name table entries
        with NameID > 18, which are expressly for localising the ASCII-only IDs
        into Hindi / Arabic / etc.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1663",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_name_ascii_only_entries(ttFont):
    """Are there non-ASCII characters in ASCII-only NAME table entries?"""
    bad_entries = []
    for name in ttFont["name"].names:
        if name.nameID in (NameID.COPYRIGHT_NOTICE, NameID.POSTSCRIPT_NAME):
            string = name.string.decode(name.getEncoding())
            try:
                string.encode("ascii")
            except UnicodeEncodeError:
                bad_entries.append(name)
                badstring = string.encode("ascii", errors="xmlcharrefreplace")
                yield FAIL, Message(
                    "bad-string",
                    (
                        f"Bad string at"
                        f" [nameID {name.nameID}, '{name.getEncoding()}']:"
                        f" '{badstring}'"
                    ),
                )
    if len(bad_entries) > 0:
        yield FAIL, Message(
            "non-ascii-strings",
            (
                f"There are {len(bad_entries)} strings containing"
                " non-ASCII characters in the ASCII-only"
                " NAME table entries."
            ),
        )


@check(
    id="name/family_and_style_max_length",
    rationale="""
        This check ensures that the length of name table entries is not
        too long, as this causes problems in some environments.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1488",
        "https://github.com/fonttools/fontbakery/issues/2179",
    ],
)
def check_name_family_and_style_max_length(ttFont):
    """Combined length of family and style must not exceed 32 characters."""

    def strip_ribbi(x):
        ribbi_re = " (" + "|".join(RIBBI_STYLE_NAMES) + ")$"
        return re.sub(ribbi_re, "", x)

    checks = [
        [
            FAIL,
            NameID.FULL_FONT_NAME,
            32,
            (
                "with the dropdown menu in old versions of Microsoft Word"
                " as well as shaping issues for some accented letters in"
                " Microsoft Word on Windows 10 and 11"
            ),
            strip_ribbi,
        ],
        [
            WARN,
            NameID.POSTSCRIPT_NAME,
            27,
            "with PostScript printers, especially on Mac platforms",
            lambda x: x,
        ],
    ]
    for loglevel, nameid, maxlen, reason, transform in checks:
        for the_name in get_name_entry_strings(ttFont, nameid):
            the_name = transform(the_name)
            if len(the_name) > maxlen:
                yield loglevel, Message(
                    f"nameid{nameid}-too-long",
                    f"Name ID {nameid} '{the_name}' exceeds"
                    f" {maxlen} characters. This has been found to"
                    f" cause problems {reason}.",
                )

    # name ID 1/16 + fvar instance name > 32 : FAIL : problems with Windows
    if "fvar" in ttFont:
        for instance in ttFont["fvar"].instances:
            for instance_name in get_name_entry_strings(
                ttFont, instance.subfamilyNameID
            ):
                typo_family_names = {
                    (r.platformID, r.platEncID, r.langID): r
                    for r in ttFont["name"].names
                    if r.nameID == 16
                }
                family_names = {
                    (r.platformID, r.platEncID, r.langID): r
                    for r in ttFont["name"].names
                    if r.nameID == 1
                }
                for platform in family_names:
                    if platform in typo_family_names:
                        family_name = typo_family_names[platform].toUnicode()
                    else:
                        family_name = family_names[platform].toUnicode()
                    full_instance_name = family_name + " " + instance_name
                    if len(full_instance_name) > 32:
                        yield FAIL, Message(
                            "instance-too-long",
                            f"Variable font instance name '{full_instance_name}'"
                            f" formed by space-separated concatenation of"
                            f" font family name (nameID {NameID.FONT_FAMILY_NAME})"
                            f" and instance subfamily nameID {instance.subfamilyNameID}"
                            f" exceeds 32 characters.\n\n"
                            f"This has been found to cause shaping issues for some"
                            f" accented letters in Microsoft Word on Windows 10 and 11.",
                        )


# FIXME: This is currently an orphan check!
@disable
@check(
    id="glyphs_file/name/family_and_style_max_length",
)
def check_glyphs_file_name_family_and_style_max_length(glyphsFile):
    """Combined length of family and style must not exceed 27 characters."""

    too_long = []
    for instance in glyphsFile.instances:
        if len(instance.fullName) > 27:
            too_long.append(instance.fullName)

    if too_long:
        too_long_list = "\n  - " + "\n  - ".join(too_long)
        yield WARN, Message(
            "too-long",
            f"The fullName length exceeds 27 chars in the"
            f" following entries:\n"
            f"{too_long_list}\n"
            f"\n"
            f"Please take a look at the conversation at"
            f" https://github.com/fonttools/fontbakery/issues/2179"
            f" in order to understand the reasoning behind these"
            f" name table records max-length criteria.",
        )


@check(
    id="name_length_req",
    rationale="""
        For Office, family and subfamily names must be 31 characters or less total
        to fit in a LOGFONT.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_length_req(ttFont):
    """Maximum allowed length for family and subfamily names."""
    family_name = get_family_name(ttFont)
    subfamily_name = get_subfamily_name(ttFont)
    if family_name is None:
        yield FAIL, "Name ID 1 (family) missing"
    if subfamily_name is None:
        yield FAIL, "Name ID 2 (sub family) missing"

    logfont = (
        family_name
        if subfamily_name in ("Regular", "Bold", "Italic", "Bold Italic")
        else " ".join([family_name, subfamily_name])
    )

    if len(logfont) > 31:
        yield FAIL, (
            f"Family + subfamily name, '{logfont}', is too long: "
            f"{len(logfont)} characters; must be 31 or less"
        )


@check(
    id="typographic_family_name",
    rationale="""
        Check whether Name ID 16 (Typographic Family name) is consistent
        across the set of fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_typographic_family_name(ttFonts):
    """Typographic Family name consistency."""
    values = set()
    for ttFont in ttFonts:
        name_record = ttFont["name"].getName(16, 3, 1, 0x0409)
        if name_record is None:
            values.add("<no value>")
        else:
            values.add(name_record.toUnicode())
    if len(values) != 1:
        yield FAIL, (
            f"Name ID 16 (Typographic Family name) is not consistent "
            f"across fonts. Values found: {sorted(values)}"
        )


@check(
    id="no_mac_entries",
    rationale="""
        Mac name table entries are not needed anymore. Even Apple stopped producing
        name tables with platform 1. Please see for example the following system font:

        /System/Library/Fonts/SFCompact.ttf

        Also, Dave Opstad, who developed Apple's TrueType specifications, told
        Olli Meier a couple years ago (as of January/2022) that these entries are
        outdated and should not be produced anymore.
    """,
    proposal="https://github.com/googlefonts/gftools/issues/469",
)
def check_name_no_mac_entries(ttFont):
    """Ensure font doesn't have Mac name table entries (platform=1)."""

    for rec in ttFont["name"].names:
        if rec.platformID == 1:
            yield FAIL, Message("mac-names", f"Please remove name ID {rec.nameID}")
