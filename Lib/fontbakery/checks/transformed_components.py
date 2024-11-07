from fontbakery.prelude import PASS, FAIL, Message, check


@check(
    id="transformed_components",
    conditions=["is_ttf"],
    rationale="""
        Some families have glyphs which have been constructed by using
        transformed components e.g the 'u' being constructed from a flipped 'n'.

        From a designers point of view, this sounds like a win (less work).
        However, such approaches can lead to rasterization issues, such as
        having the 'u' not sitting on the baseline at certain sizes after
        running the font through ttfautohint.

        Other issues are outlines that end up reversed when only one dimension
        is flipped while the other isn't.

        As of July 2019, Marc Foley observed that ttfautohint assigns cvt values
        to transformed glyphs as if they are not transformed and the result is
        they render very badly, and that vttLib does not support flipped components.

        When building the font with fontmake, the problem can be fixed by adding
        this to the command line:

        --filter DecomposeTransformedComponentsFilter
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2011",
)
def check_transformed_components(ttFont, is_hinted):
    """Ensure component transforms do not perform scaling or rotation."""
    failures = ""
    for glyph_name in ttFont.getGlyphOrder():
        glyf = ttFont["glyf"][glyph_name]
        if not glyf.isComposite():
            continue
        for component in glyf.components:
            comp_name, transform = component.getComponentInfo()

            # Font is hinted, complain about *any* transformations
            if is_hinted:
                if transform[0:4] != (1, 0, 0, 1):
                    failures += f"* {glyph_name} (component {comp_name})\n"
            # Font is unhinted, complain only about transformations where
            # only one dimension is flipped while the other isn't.
            # Otherwise the outline direction is intact and since the font is unhinted,
            # no rendering problems are to be expected
            else:
                if transform[0] * transform[3] < 0:
                    failures += f"* {glyph_name} (component {comp_name})\n"

    if failures:
        yield FAIL, Message(
            "transformed-components",
            "The following glyphs had components with scaling or rotation\n"
            f"or inverted outline direction:\n\n{failures}",
        )
    else:
        yield PASS, "No glyphs had components with scaling or rotation"
