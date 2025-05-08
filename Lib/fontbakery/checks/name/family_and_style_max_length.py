import re
from itertools import product
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
            "cause a fallback font to appear for some accented letters, as well as"
            " in some scripts such as Thai, in"
            " Microsoft Word on Windows 10 and 11. It can also lead to names"
            " which are truncated in the Microsoft Word font menu.\n\n",
            strip_ribbi,
        ],
        [
            WARN,
            NameID.POSTSCRIPT_NAME,
            27,
            "with PostScript printers, especially on Mac platforms. Per Thomas"
            " Phinney, this is likely limited to classic versions "
            " of Mac OS, pre-OS X (released in the year 2000).\n\n",
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

    # check variable font name lengths
    if "fvar" in ttFont and "STAT" in ttFont:

        # get the family name from the name table (prefer ID 16)
        try:
            family_name = ttFont["name"].getName(NameID.TYPOGRAPHIC_FAMILY_NAME, 3, 1, 0x409).toUnicode()
            family_name_id = NameID.TYPOGRAPHIC_FAMILY_NAME
        except AttributeError:
            family_name = ttFont["name"].getName(NameID.FONT_FAMILY_NAME, 3, 1, 0x409).toUnicode()
            family_name_id = NameID.FONT_FAMILY_NAME

        styles_per_axis = defaultdict(list)
        for value in ttFont["STAT"].table.AxisValueArray.AxisValue:
            # if the value is marked as elidable, don’t count it
            if value.Flags & 2:
                continue
            # otherwise, get the STAT style particle name and add it to the list
            styles_per_axis[value.AxisIndex].append(
                ttFont["name"].getName(value.ValueNameID, 3, 1, 0x409).toUnicode()
            )

        # make list of combined family & STAT style names
        names = [
            f'{family_name} {" ".join(combination)}'
            for combination in product(*styles_per_axis.values())
        ]

        for name in names:
            if len(name) > 31:
                stat_style_combination = name.replace(f"{family_name} ", "")
                yield FAIL, Message(
                    "familyname-plus-stat-entries-too-long",
                    f"Name ID {family_name_id} '{family_name}' plus"
                    f" STAT table style combination '{stat_style_combination}'"
                    f" exceeds 31 characters (the combination is {len(name)} characters in total).\n\n"
                    f" This has been found to"
                    f" cause a fallback font to appear for some accented letters, as well as"
                    f" in some scripts such as Thai, in"
                    f" Microsoft Word on Windows 10 and 11. It can also lead to names"
                    f" which are truncated in the Microsoft Word font menu.\n\n",
                )

    # if STAT not in font, assume that "fvar" instance names are used
    if "fvar" in ttFont and "STAT" not in ttFont:
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
                            "fvar-instance-too-long",
                            f"Variable font instance name '{full_instance_name}'"
                            f" formed by space-separated concatenation of"
                            f" font family name (nameID {NameID.FONT_FAMILY_NAME})"
                            f" and instance subfamily nameID {instance.subfamilyNameID}"
                            f" exceeds 32 characters.\n\n"
                            f" This has been found to"
                            f" cause a fallback font to appear for some accented letters, as well as"
                            f" in some scripts such as Thai, in"
                            f" Microsoft Word on Windows 10 and 11. It can also lead to names"
                            f" which are truncated in the Microsoft Word font menu.\n\n",
                        )