from fontbakery.prelude import check, Message, FAIL
from fontbakery.checks.vendorspecific.googlefonts.utils import GFAxisRegistry


@check(
    id="googlefonts/metadata/axisregistry_bounds",
    rationale="""
        Each axis range in a METADATA.pb file must be registered, and within the bounds
        of the axis definition in the Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry
    """,
    conditions=["is_variable_font", "family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3010",
)
def check_axisregistry_bounds(family_metadata):
    """Validate METADATA.pb axes values are within gf_axisregistry bounds."""
    for axis in family_metadata.axes:
        if axis.tag in GFAxisRegistry().keys():
            expected = GFAxisRegistry()[axis.tag]
            if (
                axis.min_value < expected.min_value
                or axis.max_value > expected.max_value
            ):
                yield FAIL, Message(
                    "bad-axis-range",
                    f"The range in the font variation axis"
                    f" '{axis.tag}' ({expected.display_name}"
                    f" min:{axis.min_value} max:{axis.max_value})"
                    f" does not comply with the expected maximum range,"
                    f" as defined on Google Fonts Axis Registry"
                    f" (min:{expected.min_value} max:{expected.max_value}).",
                )
