from fontbakery.testable import Ufo
from fontbakery.prelude import check, PASS, WARN, Message
from fontbakery import utils


@check(
    id="ufo_consistent_curve_type",
    rationale="""
        This is normally an accident, and may be handled incorrectly by the
        build pipeline unless specifically configured to account for this.
    """,
    conditions=["ufo_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/4795",
)
def check_ufo_consistent_curve_type(config, ufo: Ufo):
    """Check that all glyphs across the source use the same curve type"""

    cubic_glyphs = []
    quadratic_glyphs = []
    mixed_glyphs = []
    for layer in ufo.ufo_font.layers:  # type: ignore
        for glyph in layer:
            point_types = set(
                point.segmentType for contour in glyph for point in contour
            )
            if "curve" in point_types and "qcurve" in point_types:
                mixed_glyphs.append(glyph.name)
            elif "curve" in point_types:
                cubic_glyphs.append(glyph.name)
            elif "qcurve" in point_types:
                quadratic_glyphs.append(glyph.name)

    if mixed_glyphs:
        yield (
            WARN,
            Message(
                "mixed-glyphs",
                f"UFO contains glyphs with mixed curves:\n\n"
                f"{utils.bullet_list(config, mixed_glyphs)}\n",
            ),
        )
    if cubic_glyphs and quadratic_glyphs:
        yield (
            WARN,
            Message(
                "both-cubic-and-quadratic",
                f"UFO contains a mix of cubic-curve glyphs"
                f" and quadratic-curve glyphs\n\n"
                f"Cubics:\n\n"
                f"{utils.bullet_list(config, cubic_glyphs)}\n\n"
                f"Quadratics:\n\n"
                f"{utils.bullet_list(config, quadratic_glyphs)}\n",
            ),
        )
    elif not mixed_glyphs:
        yield PASS, "All curves of all glyphs use a consistent curve type"
