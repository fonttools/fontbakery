from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/glyf_non_transformed_duplicate_components",
    rationale="""
        There have been cases in which fonts had faulty double quote marks, with each
        of them containing two single quote marks as components with the same
        x, y coordinates which makes them visually look like single quote marks.

        This check ensures that glyphs do not contain duplicate components
        which have the same x,y coordinates.
    """,
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/pull/2709",
)
def check_glyf_non_transformed_duplicate_components(ttFont, config):
    """
    Check glyphs do not have duplicate components which have the same x,y coordinates.
    """
    from fontbakery.utils import pretty_print_list

    failed = []
    for glyph_name in ttFont["glyf"].keys():
        glyph = ttFont["glyf"][glyph_name]
        if not glyph.isComposite():
            continue

        seen = []
        for comp in glyph.components:
            comp_info = {
                "glyph": glyph_name,
                "component": comp.glyphName,
                "x": comp.x,
                "y": comp.y,
            }
            if comp_info in seen:
                failed.append(comp_info)
            else:
                seen.append(comp_info)
    if failed:
        formatted_list = "\t* " + pretty_print_list(config, failed, sep="\n\t* ")
        yield FAIL, Message(
            "found-duplicates",
            f"The following glyphs have duplicate components which"
            f" have the same x,y coordinates:\n"
            f"{formatted_list}",
        )
