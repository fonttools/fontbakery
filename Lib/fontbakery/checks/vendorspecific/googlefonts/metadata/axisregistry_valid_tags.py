from fontbakery.prelude import check, Message, FAIL
from fontbakery.checks.vendorspecific.googlefonts.utils import GFAxisRegistry


@check(
    id="googlefonts/metadata/axisregistry_valid_tags",
    rationale="""
        Ensure all axes in a METADATA.pb file are registered in the
        Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry

        Why does Google Fonts have its own Axis Registry?

        We support a superset of the OpenType axis registry axis set, and use
        additional metadata for each axis. Axes present in a font file but not in this
        registry will not function via our API. No variable font is expected to
        support all of the axes here.

        Any font foundry or distributor library that offers variable fonts has a
        implicit, latent, de-facto axis registry, which can be extracted by scanning
        the library for axes' tags, labels, and min/def/max values. While in 2016
        Microsoft originally offered to include more axes in the OpenType 1.8
        specification (github.com/microsoft/OpenTypeDesignVariationAxisTags), as of
        August 2020, this effort has stalled. We hope more foundries and distributors
        will publish documents like this that make their axes explicit, to encourage
        of adoption of variable fonts throughout the industry, and provide source
        material for a future update to the OpenType specification's axis registry.
    """,
    conditions=["is_variable_font", "family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3022",
)
def check_axisregistry_valid_tags(family_metadata):
    """Validate METADATA.pb axes tags are defined in gf_axisregistry."""
    for axis in family_metadata.axes:
        if axis.tag not in GFAxisRegistry().keys():
            yield FAIL, Message(
                "bad-axis-tag",
                f"The font variation axis '{axis.tag}'"
                f" is not yet registered on Google Fonts Axis Registry.",
            )
