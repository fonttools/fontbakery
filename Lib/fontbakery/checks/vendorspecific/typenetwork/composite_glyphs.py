import string

from fontbakery.prelude import check, Message, PASS, WARN


@check(
    id="typenetwork/composite_glyphs",
    rationale="""
        For performance reasons, it is recommended that TTF fonts use composite glyphs.
    """,
    conditions=["is_ttf"],
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_composite_glyphs(ttFont):
    """Check if TTF font uses composite glyphs."""
    baseGlyphs = [*string.printable]
    failed = []

    numberOfGlyphs = ttFont["maxp"].numGlyphs
    for glyph_name in ttFont["glyf"].keys():
        glyph = ttFont["glyf"][glyph_name]
        if glyph_name not in baseGlyphs and glyph.isComposite() is False:
            failed.append(glyph_name)

    percentageOfNotCompositeGlyphs = round(len(failed) * 100 / numberOfGlyphs)
    if percentageOfNotCompositeGlyphs > 50:
        yield WARN, Message(
            "low-composites",
            f"{percentageOfNotCompositeGlyphs}% of the glyphs are not composites.",
        )
    else:
        yield PASS, (
            f"{100-percentageOfNotCompositeGlyphs}% of the glyphs are composites."
        )
