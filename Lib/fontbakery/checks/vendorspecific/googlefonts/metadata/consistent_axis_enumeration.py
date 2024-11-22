from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import pretty_print_list


@check(
    id="googlefonts/metadata/consistent_axis_enumeration",
    rationale="""
        All font variation axes present in the font files must be properly declared
        on METADATA.pb so that they can be served by the GFonts API.
    """,
    conditions=["is_variable_font", "family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3051",
)
def check_metadata_consistent_axis_enumeration(family_metadata, ttFont, config):
    """Validate VF axes match the ones declared on METADATA.pb."""

    md_axes = set(axis.tag for axis in family_metadata.axes)
    fvar_axes = set(axis.axisTag for axis in ttFont["fvar"].axes)
    missing = sorted(fvar_axes - md_axes)
    extra = sorted(md_axes - fvar_axes)

    if missing:
        yield FAIL, Message(
            "missing-axes",
            f"The font variation axes {pretty_print_list(config, missing)}"
            f" are present in the font's fvar table but are not"
            f" declared on the METADATA.pb file.",
        )

    if extra:
        yield FAIL, Message(
            "extra-axes",
            f"The METADATA.pb file lists font variation axes that"
            f" are not supported but this family: {pretty_print_list(config, extra)}",
        )
