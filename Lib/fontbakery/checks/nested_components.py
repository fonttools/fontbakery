from fontbakery.prelude import check, Message, FAIL


@check(
    id="nested_components",
    rationale="""
        There have been bugs rendering variable fonts with nested components.
        Additionally, some static fonts with nested components have been reported
        to have rendering and printing issues.

        For more info, see:
        * https://github.com/fonttools/fontbakery/issues/2961
        * https://github.com/arrowtype/recursive/issues/412
    """,
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/issues/2961",
)
def check_nested_components(ttFont, config):
    """Ensure glyphs do not have components which are themselves components."""
    from fontbakery.utils import pretty_print_list

    bad_glyphs = []
    for glyph_name in ttFont["glyf"].keys():
        glyph = ttFont["glyf"][glyph_name]
        if not glyph.isComposite():
            continue
        for comp in glyph.components:
            if ttFont["glyf"][comp.glyphName].isComposite():
                bad_glyphs.append(glyph_name)
    if bad_glyphs:
        formatted_list = "\t* " + pretty_print_list(config, bad_glyphs, sep="\n\t* ")
        yield FAIL, Message(
            "found-nested-components",
            f"The following glyphs have components which"
            f" themselves are component glyphs:\n"
            f"{formatted_list}",
        )
