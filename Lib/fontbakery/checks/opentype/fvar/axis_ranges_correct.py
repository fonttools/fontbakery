from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.utils import get_name_entry_strings


@check(
    id="opentype/fvar/axis_ranges_correct",
    rationale="""
        According to the OpenType spec's registered design-variation tags, instances in
        a variable font should have certain prescribed values.
        If a variable font has a 'wght' (Weight) axis, the valid coordinate range is 1-1000.
        If a variable font has a 'wdth' (Width) axis, the valid numeric range is strictly greater than zero.
        If a variable font has a 'slnt' (Slant) axis, then the coordinate of its 'Regular' instance is required to be 0.
        If a variable font has a 'ital' (Slant) axis, then the coordinate of its 'Regular' instance is required to be 0.
    """,
    conditions=["is_variable_font"],
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/2264",
        "https://github.com/fonttools/fontbakery/pull/2520",
        "https://github.com/fonttools/fontbakery/issues/2572",
    ],
)
def check_fvar_axis_ranges_correct(ttFont, ital_axis, slnt_axis):
    """Axes and named instances fall within correct ranges?"""

    for instance in ttFont["fvar"].instances:
        name = get_name_entry_strings(ttFont, instance.subfamilyNameID)[0]

        if "wght" in instance.coordinates:
            value = instance.coordinates["wght"]
            if value < 1 or value > 1000:
                yield FAIL, Message(
                    "wght-out-of-range",
                    f"Instance {name} has wght coordinate"
                    f" of {value}, expected between 1 and 1000",
                )
                break

        if "wdth" in instance.coordinates:
            value = instance.coordinates["wdth"]
            if value < 1:
                yield FAIL, Message(
                    "wdth-out-of-range",
                    f"Instance {name} has wdth coordinate"
                    f" of {value}, expected at least 1",
                )
                break

            if value > 1000:
                yield WARN, Message(
                    "wdth-greater-than-1000",
                    f"Instance {name} has wdth coordinate"
                    f" of {value}, which is valid but unusual",
                )
                break

    if ital_axis:
        if not (ital_axis.minValue == 0 and ital_axis.maxValue == 1):
            yield FAIL, Message(
                "invalid-ital-range",
                f'The range of values for the "ital" axis in this font is'
                f" {ital_axis.minValue} to {ital_axis.maxValue}."
                f" The italic axis range must be 0 to 1, where Roman is 0 and Italic 1."
                f' If you prefer a bigger variation range consider using the "Slant"'
                f' axis instead of "Italic".',
            )

    if slnt_axis:
        if not (slnt_axis.minValue < 0 and slnt_axis.maxValue >= 0):
            yield WARN, Message(
                "unusual-slnt-range",
                f'The range of values for the "slnt" axis in this font only allows'
                f" positive coordinates (from {slnt_axis.minValue} to"
                f" {slnt_axis.maxValue}), indicating that this may be a back slanted"
                f' design, which is rare. If that\'s not the case, then the "slant"'
                f" axis should be a range of negative values instead.",
            )
