from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/cff_call_depth",
    conditions=["ttFont", "is_cff"],
    rationale="""
        Per "The Type 2 Charstring Format, Technical Note #5177",
        the "Subr nesting, stack limit" is 10.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2425",
)
def check_cff_call_depth(font):
    """Is the CFF subr/gsubr call depth > 10?"""
    analysis = font.cff_analysis

    if analysis.glyphs_exceed_max or analysis.glyphs_recursion_errors:
        for gn in analysis.glyphs_exceed_max:
            yield FAIL, Message(
                "max-depth",
                f'Subroutine call depth exceeded maximum of 10 for glyph "{gn}".',
            )
        for gn in analysis.glyphs_recursion_errors:
            yield FAIL, Message(
                "recursion-error", f'Recursion error while decompiling glyph "{gn}".'
            )
