from fontbakery.prelude import check, Message, INFO, FAIL, WARN


@check(
    id="googlefonts/gasp",
    conditions=["is_ttf"],
    rationale="""
        Traditionally version 0 'gasp' tables were set so that font sizes below 8 ppem
        had no grid fitting but did have antialiasing. From 9-16 ppem, just grid
        fitting.
        And fonts above 17ppem had both antialiasing and grid fitting toggled on.
        The use of accelerated graphics cards and higher resolution screens make this
        approach obsolete. Microsoft's DirectWrite pushed this even further with much
        improved rendering built into the OS and apps.

        In this scenario it makes sense to simply toggle all 4 flags ON for all font
        sizes.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_gasp(ttFont):
    """Is the Grid-fitting and Scan-conversion Procedure ('gasp') table
    set to optimize rendering?"""

    NON_HINTING_MESSAGE = (
        "If you are dealing with an unhinted font,"
        " it can be fixed by running the fonts through"
        " the command 'gftools fix-nonhinting'\n"
        "GFTools is available at"
        " https://pypi.org/project/gftools/"
    )

    if "gasp" not in ttFont.keys():
        yield FAIL, Message(
            "lacks-gasp",
            "Font is missing the 'gasp' table."
            " Try exporting the font with autohinting enabled.\n" + NON_HINTING_MESSAGE,
        )
    else:
        if not isinstance(ttFont["gasp"].gaspRange, dict):
            yield FAIL, Message(
                "empty", "The 'gasp' table has no values.\n" + NON_HINTING_MESSAGE
            )
        else:
            if 0xFFFF not in ttFont["gasp"].gaspRange:
                yield WARN, Message(
                    "lacks-ffff-range",
                    "The 'gasp' table does not have an entry"
                    " that applies for all font sizes."
                    " The gaspRange value for such entry should"
                    " be set to 0xFFFF.",
                )
            else:
                gasp_meaning = {
                    0x01: "- Use grid-fitting",
                    0x02: "- Use grayscale rendering",
                    0x04: "- Use gridfitting with ClearType symmetric smoothing",
                    0x08: "- Use smoothing along multiple axes with ClearType®",
                }
                table = []
                for key in ttFont["gasp"].gaspRange.keys():
                    value = ttFont["gasp"].gaspRange[key]
                    meaning = []
                    for flag, info in gasp_meaning.items():
                        if value & flag:
                            meaning.append(info)

                    meaning = "\n\t".join(meaning)
                    table.append(f"PPM <= {key}:\n\tflag = 0x{value:02X}\n\t{meaning}")

                table = "\n".join(table)
                yield INFO, Message(
                    "ranges",
                    f"These are the ppm ranges declared on"
                    f" the gasp table:\n\n{table}\n",
                )

                for key in ttFont["gasp"].gaspRange.keys():
                    if key != 0xFFFF:
                        yield WARN, Message(
                            "non-ffff-range",
                            f"The gasp table has a range of {key}"
                            f" that may be unneccessary.",
                        )
                    else:
                        value = ttFont["gasp"].gaspRange[0xFFFF]
                        if value != 0x0F:
                            yield WARN, Message(
                                "unset-flags",
                                f"The gasp range 0xFFFF value 0x{value:02X}"
                                f" should be set to 0x0F.",
                            )
