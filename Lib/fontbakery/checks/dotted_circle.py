from fontbakery.prelude import check, FAIL, PASS, SKIP, WARN, Message
from fontbakery.checks.shaping.utils import is_complex_shaper_font


@check(
    id="dotted_circle",
    conditions=["is_ttf"],
    severity=3,
    rationale="""
        The dotted circle character (U+25CC) is inserted by shaping engines before
        mark glyphs which do not have an associated base, especially in the context
        of broken syllabic clusters.

        For fonts containing combining marks, it is recommended that the dotted circle
        character be included so that these isolated marks can be displayed properly;
        for fonts supporting complex scripts, this should be considered mandatory.

        Additionally, when a dotted circle glyph is present, it should be able to
        display all marks correctly, meaning that it should contain anchors for all
        attaching marks.

        A fontmake filter can be used to automatically add a dotted_circle to a font:

        fontmake --filter 'DottedCircleFilter(pre=True)' --filter '...'
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3600",
)
def check_dotted_circle(ttFont, config):
    """Ensure dotted circle glyph is present and can attach marks."""
    from fontbakery.utils import bullet_list, iterate_lookup_list_with_extensions

    mark_glyphs = []
    if (
        "GDEF" in ttFont
        and hasattr(ttFont["GDEF"].table, "GlyphClassDef")
        and hasattr(ttFont["GDEF"].table.GlyphClassDef, "classDefs")
    ):
        mark_glyphs = [
            k for k, v in ttFont["GDEF"].table.GlyphClassDef.classDefs.items() if v == 3
        ]

    # Only check for encoded
    mark_glyphs = set(mark_glyphs) & set(ttFont.getBestCmap().values())
    nonspacing_mark_glyphs = [g for g in mark_glyphs if ttFont["hmtx"][g][0] == 0]

    if not nonspacing_mark_glyphs:
        yield SKIP, "Font has no nonspacing mark glyphs."
        return

    if 0x25CC not in ttFont.getBestCmap():
        # How bad is this?
        if is_complex_shaper_font(ttFont):
            yield FAIL, Message(
                "missing-dotted-circle-complex",
                "No dotted circle glyph present and font uses a complex shaper",
            )
        else:
            yield WARN, Message(
                "missing-dotted-circle", "No dotted circle glyph present"
            )
        return

    # Check they all attach to dotted circle
    # if they attach to something else
    dotted_circle = ttFont.getBestCmap()[0x25CC]
    attachments = {dotted_circle: []}
    does_attach = {}

    def find_mark_base(lookup, attachments):
        if lookup.LookupType == 4:
            # Assume all-to-all
            for st in lookup.SubTable:
                for base in st.BaseCoverage.glyphs:
                    for mark in st.MarkCoverage.glyphs:
                        attachments.setdefault(base, []).append(mark)
                        does_attach[mark] = True

    iterate_lookup_list_with_extensions(ttFont, "GPOS", find_mark_base, attachments)

    unattached = []
    for g in nonspacing_mark_glyphs:
        if g in does_attach and g not in attachments[dotted_circle]:
            unattached.append(g)

    if unattached:
        yield FAIL, Message(
            "unattached-dotted-circle-marks",
            f"The following glyphs could not be attached to the dotted circle glyph:\n\n"
            f"{bullet_list(config, sorted(unattached))}",
        )
    else:
        yield PASS, "All marks were anchored to dotted circle"
