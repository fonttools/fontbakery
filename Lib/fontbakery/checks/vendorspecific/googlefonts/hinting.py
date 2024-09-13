from fontbakery.prelude import check, Message, INFO, PASS, FAIL, WARN, SKIP
from fontbakery.constants import LATEST_TTFAUTOHINT_VERSION, NameID


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


@check(
    id="googlefonts/has_ttfautohint_params",
    proposal="https://github.com/fonttools/fontbakery/issues/1773",
    rationale="""
        It is critically important that all static TTFs in the Google Fonts API
        which were autohinted with ttfautohint store their TTFAutohint args in
        the 'name' table, so that an automated solution can be made to
        replicate the hinting on subsets, etc.
    """,
)
def check_has_ttfautohint_params(ttFont):
    """Font has ttfautohint params?"""
    from fontbakery.utils import get_name_entry_strings

    def ttfautohint_version(value):
        # example string:
        # 'Version 1.000; ttfautohint (v0.93) -l 8 -r 50 -G 200 -x 14 -w "G"
        import re

        results = re.search(r"ttfautohint \(v(.*)\) ([^;]*)", value)
        if results:
            return results.group(1), results.group(2)

    version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    passed = False
    for vstring in version_strings:
        values = ttfautohint_version(vstring)
        if values:
            ttfa_version, params = values
            if params:
                passed = True
                yield PASS, Message("ok", f"Font has ttfautohint params ({params})")
        else:
            passed = True
            yield SKIP, Message(
                "not-hinted",
                "Font appears to our heuristic as not hinted using ttfautohint.",
            )

    if not passed:
        yield FAIL, Message(
            "lacks-ttfa-params",
            "Font is lacking ttfautohint params on its"
            " version strings on the name table.",
        )


@check(
    id="googlefonts/old_ttfautohint",
    conditions=["is_ttf"],
    rationale="""
        Check if font has been hinted with an outdated version of ttfautohint.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_old_ttfautohint(ttFont):
    """Font has old ttfautohint applied?"""
    from fontbakery.utils import get_name_entry_strings

    def ttfautohint_version(values):
        import re

        for value in values:
            results = re.search(r"ttfautohint \(v(.*)\)", value)
            if results:
                return results.group(1)

    version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    ttfa_version = ttfautohint_version(version_strings)
    if len(version_strings) == 0:
        yield FAIL, Message(
            "lacks-version-strings",
            "This font file lacks mandatory version strings in its name table.",
        )
    elif ttfa_version is None:
        yield INFO, Message(
            "version-not-detected",
            f"Could not detect which version of"
            f" ttfautohint was used in this font."
            f" It is typically specified as a comment"
            f" in the font version entries of the 'name' table."
            f" Such font version strings are currently:"
            f" {version_strings}",
        )
    else:
        try:
            if LATEST_TTFAUTOHINT_VERSION > ttfa_version:
                yield WARN, Message(
                    "old-ttfa",
                    f"ttfautohint used in font = {ttfa_version};"
                    f" latest = {LATEST_TTFAUTOHINT_VERSION};"
                    f" Need to re-run with the newer version!",
                )
        except ValueError:
            yield FAIL, Message(
                "parse-error",
                f"Failed to parse ttfautohint version values:"
                f" latest = '{LATEST_TTFAUTOHINT_VERSION}';"
                f" used_in_font = '{ttfa_version}'",
            )
