from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="opentype/varfont/ital_range",
    rationale="""
        The OpenType spec says at
        https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_ital
        that:

        [...] Valid numeric range: Values must be in the range 0 to 1.
    """,
    conditions=["is_variable_font", "has_ital_axis"],
)
def check_varfont_ital_range(ttFont, ital_axis):
    """The variable font 'ital' (Italic) axis coordinates
    is in a valid range?"""

    if not (ital_axis.minValue == 0 and ital_axis.maxValue == 1):
        yield FAIL, Message(
            "invalid-ital-range",
            f'The range of values for the "ital" axis in'
            f" this font is {ital_axis.minValue} to {ital_axis.maxValue}."
            f" Italic axis range must be 0 to 1, "
            f" where Roman is 0 and Italic 1."
            f" If you prefer a bigger variation range consider using"
            f' "Slant" axis instead of "Italic".',
        )


@check(
    id="opentype/varfont/slnt_range",
    rationale="""
        The OpenType spec says at
        https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt that:

        [...] the scale for the Slant axis is interpreted as the angle of slant
        in counter-clockwise degrees from upright. This means that a typical,
        right-leaning oblique design will have a negative slant value. This matches
        the scale used for the italicAngle field in the post table.
    """,
    conditions=["is_variable_font", "has_slnt_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/2572",
)
def check_varfont_slnt_range(ttFont, slnt_axis):
    """The variable font 'slnt' (Slant) axis coordinate
    specifies positive values in its range?"""

    if not (slnt_axis.minValue < 0 and slnt_axis.maxValue >= 0):
        yield WARN, Message(
            "unusual-slnt-range",
            f'The range of values for the "slnt" axis in'
            f" this font only allows positive coordinates"
            f" (from {slnt_axis.minValue} to {slnt_axis.maxValue}),"
            f" indicating that this may be a back slanted design,"
            f" which is rare. If that's not the case, then"
            f' the "slant" axis should be a range of'
            f" negative values instead.",
        )


@check(
    id="opentype/varfont/wght_valid_range",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'wght' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wght

        On the 'wght' (Weight) axis, the valid coordinate range is 1-1000.
    """,
    conditions=["is_variable_font", "has_wght_axis"],
    proposal="https://github.com/fonttools/fontbakery/issues/2264",
)
def check_varfont_wght_valid_range(ttFont):
    """The variable font 'wght' (Weight) axis coordinate
    must be within spec range of 1 to 1000 on all instances."""

    for instance in ttFont["fvar"].instances:
        if "wght" in instance.coordinates:
            value = instance.coordinates["wght"]
            if value < 1 or value > 1000:
                yield FAIL, Message(
                    "wght-out-of-range",
                    f'Found a bad "wght" coordinate with value {value}'
                    f" outside of the valid range from 1 to 1000.",
                )
                break


@check(
    id="opentype/varfont/wdth_valid_range",
    rationale="""
        According to the OpenType spec's
        registered design-variation tag 'wdth' available at
        https://docs.microsoft.com/en-gb/typography/opentype/spec/dvaraxistag_wdth

        On the 'wdth' (Width) axis, the valid numeric range is strictly greater than
        zero.
    """,
    conditions=["is_variable_font", "has_wdth_axis"],
    proposal="https://github.com/fonttools/fontbakery/pull/2520",
)
def check_varfont_wdth_valid_range(ttFont):
    """The variable font 'wdth' (Width) axis coordinate
    must strictly greater than zero."""

    for instance in ttFont["fvar"].instances:
        if "wdth" in instance.coordinates:
            value = instance.coordinates["wdth"]
            if value < 1:
                yield FAIL, Message(
                    "wdth-out-of-range",
                    f'Found a bad "wdth" coordinate with value {value}'
                    f" outside of the valid range (> 0).",
                )
                break

            if value > 1000:
                yield WARN, Message(
                    "wdth-greater-than-1000",
                    f'Found a "wdth" coordinate with value {value}'
                    f" which is valid but unusual.",
                )
                break
