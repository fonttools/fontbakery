from fontbakery.prelude import check, condition, Message, FAIL, PASS
from fontbakery.testable import Font


@condition(Font)
def uharfbuzz_blob(font):
    import uharfbuzz as hb

    return hb.Blob.from_file_path(font.file)


@check(
    id="opentype/slant_direction",
    conditions=["is_variable_font"],
    rationale="""
        The 'slnt' axis values are defined as negative values for a clockwise (right)
        lean, and positive values for counter-clockwise lean. This is counter-intuitive
        for many designers who are used to think of a positive slant as a lean to
        the right.

        This check ensures that the slant axis direction is consistent with the specs.

        https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_slnt
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3910",
)
def check_slant_direction(ttFont, uharfbuzz_blob):
    """Checking direction of slnt axis angles."""
    import uharfbuzz as hb
    from fontbakery.utils import PointsPen, axis

    if not axis(ttFont, "slnt"):
        yield PASS, "Font has no slnt axis"
        return

    hb_face = hb.Face(uharfbuzz_blob)
    hb_font = hb.Font(hb_face)
    buf = hb.Buffer()
    buf.add_str("H")
    features = {"kern": True, "liga": True}
    hb.shape(hb_font, buf, features)

    def x_delta(slant):
        """
        Return the x delta (difference of x position between highest and lowest point)
        for the given slant value.
        """
        hb_font.set_variations({"slnt": slant})
        pen = PointsPen()
        hb_font.draw_glyph_with_pen(buf.glyph_infos[0].codepoint, pen)
        x_delta = pen.highestPoint()[0] - pen.lowestPoint()[0]
        return x_delta

    if x_delta(axis(ttFont, "slnt").minValue) < x_delta(axis(ttFont, "slnt").maxValue):
        yield FAIL, Message(
            "positive-value-for-clockwise-lean",
            "The right-leaning glyphs have a positive 'slnt' axis value,"
            " which is likely a mistake. It needs to be negative"
            " to lean rightwards.",
        )
