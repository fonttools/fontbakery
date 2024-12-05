from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import (
    bullet_list,
    close_but_not_on,
)
from fontbakery.checks.outline_settings import (
    ALIGNMENT_MISS_EPSILON,
    FALSE_POSITIVE_CUTOFF,
)


@check(
    id="outline_alignment_miss",
    rationale=f"""
        This check heuristically looks for on-curve points which are close to, but
        do not sit on, significant boundary coordinates. For example, a point which
        has a Y-coordinate of 1 or -1 might be a misplaced baseline point. As well as
        the baseline, here we also check for points near the x-height (but only for
        lowercase Latin letters), cap-height, ascender and descender Y coordinates.

        Not all such misaligned curve points are a mistake, and sometimes the design
        may call for points in locations near the boundaries. As this check is liable
        to generate significant numbers of false positives, it will pass if there are
        more than {FALSE_POSITIVE_CUTOFF} reported misalignments.
    """,
    conditions=["outlines_dict"],
    proposal="https://github.com/fonttools/fontbakery/pull/3088",
)
def check_outline_alignment_miss(ttFont, outlines_dict, config):
    """Are there any misaligned on-curve points?"""

    warnings = []

    alignments = {
        "baseline": 0,
        "ascender": ttFont["OS/2"].sTypoAscender,
        "descender": ttFont["OS/2"].sTypoDescender,
    }

    # The x-height and cap-height checks (which are useful)
    # use the xHeight and CapHeight fields in the OS/2 table.
    # Those fields are available from version 2 onwards.
    # Any modern font will generally be version 4 or higher, but
    # some historical or otherwise esoteric fonts may have an
    # earlier versioned OS/2 table.
    os2version = ttFont["OS/2"].version
    if os2version >= 2:
        alignments["x-height"] = ttFont["OS/2"].sxHeight
        alignments["cap-height"] = ttFont["OS/2"].sCapHeight
    else:
        yield WARN, Message(
            "skip-cap-x-height-alignment",
            "x-height and cap-height checks are skipped"
            f" because OS/2 table version is only {os2version}"
            " and version >= 2 is required for those checks.",
        )

    for glyph, outlines in outlines_dict.items():
        glyphname, display_name = glyph
        for p in outlines:
            for node in p.asNodelist():
                if node.type == "offcurve":
                    continue
                for line, yExpected in alignments.items():
                    # skip x-height check for caps
                    if line == "x-height" and (
                        len(glyphname) > 1 or glyphname[0].isupper()
                    ):
                        continue
                    if close_but_not_on(yExpected, node.y, ALIGNMENT_MISS_EPSILON):
                        warnings.append(
                            f"{display_name}: X={node.x},Y={node.y}"
                            f" (should be at {line} {yExpected}?)"
                        )
        if len(warnings) > FALSE_POSITIVE_CUTOFF:
            # Let's not waste time.
            yield PASS, (
                "So many Y-coordinates of points were close to"
                " boundaries that this was probably by design."
            )
            return

    if warnings:
        formatted_list = bullet_list(config, warnings, bullet="*")
        yield WARN, Message(
            "found-misalignments",
            f"The following glyphs have on-curve points which"
            f" have potentially incorrect y coordinates:\n\n"
            f"{formatted_list}",
        )
    else:
        yield PASS, "Y-coordinates of points fell on appropriate boundaries."
