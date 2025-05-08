import re
from collections import defaultdict

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
    """Combined length of family and style must not exceed 31 characters."""

    def strip_ribbi(x):
        ribbi_re = " (" + "|".join(RIBBI_STYLE_NAMES) + ")$"
        return re.sub(ribbi_re, "", x)

    checks = [
        [
            FAIL,
            NameID.FONT_FAMILY_NAME,
            31,
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

        try:
            family_name = ttFont["name"].getName(NameID.TYPOGRAPHIC_FAMILY_NAME, 3, 1, 0x409).toUnicode()
            family_name_id = NameID.TYPOGRAPHIC_FAMILY_NAME
        except AttributeError:
            family_name = ttFont["name"].getName(NameID.FONT_FAMILY_NAME, 3, 1, 0x409).toUnicode()
            family_name_id = NameID.FONT_FAMILY_NAME


        styles_per_axis = defaultdict(list)
        for value in font["STAT"].table.AxisValueArray.AxisValue:
            axis_name = axes[value.AxisIndex]
            styles_per_axis[axis_name].append(
                font["name"].getName(value.ValueNameID, 3, 1, 0x409).toUnicode()
            )

        names = [
            f'{family_name} {" ".join(combination)}'
            for combination in product(*styles_per_axis.values())
        ]

        for name in names:
            if len(name) > 31:
                stat_style_combination = name.remove(family_name + " ")
                yield FAIL, Message(
                    "familyname-plus-stat-entries-too-long",
                    f"Name ID {family_name_id} '{name}' plus"
                    f" STAT table style combination '{stat_style_combination}'"
                    f" exceeds 31 characters.\n\n This has been found to"
                    f" cause a fallback font to appear for some accented letters in"
                    f" Microsoft Word on Windows 10 and 11.",
                )