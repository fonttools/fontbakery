import re

from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
)
from fontbakery.prelude import check, disable, Message, FAIL, WARN
from fontbakery.utils import get_name_entry_strings


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
        "legacy:check/074",
        "https://github.com/fonttools/fontbakery/issues/1663",
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

    # name ID 1 + fvar instance name > 32 : FAIL : problems with Windows
    if "fvar" in ttFont:
        for instance in ttFont["fvar"].instances:
            for instance_name in get_name_entry_strings(
                ttFont, instance.subfamilyNameID
            ):
                for family_name in get_name_entry_strings(
                    ttFont, NameID.FONT_FAMILY_NAME
                ):
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
