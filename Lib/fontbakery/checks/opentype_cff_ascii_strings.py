from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/cff_ascii_strings",
    conditions=["ttFont", "is_cff", "cff_analysis"],
    rationale="""
        All CFF Table top dict string chars should fit into the ASCII range.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4619",
)
def check_cff_ascii_strings(cff_analysis):
    """Does the font's CFF table top dict strings fit into the ASCII range?"""

    if cff_analysis.string_not_ascii is None:
        yield FAIL, Message(
            "cff-unable-to-decode",
            "Unable to decode CFF table, possibly due to out"
            " of ASCII range strings. Please check table strings.",
        )
    elif cff_analysis.string_not_ascii:
        detailed_info = ""
        for key, string in cff_analysis.string_not_ascii:
            detailed_info += (
                f"\n\n\t - {key}: {string.encode('latin-1').decode('utf-8')}"
            )

        yield FAIL, Message(
            "cff-string-not-in-ascii-range",
            f"The following CFF TopDict strings"
            f" are not in the ASCII range: {detailed_info}",
        )
