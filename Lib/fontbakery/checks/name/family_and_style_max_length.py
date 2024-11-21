import re

from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
)
from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import get_name_entry_strings


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
