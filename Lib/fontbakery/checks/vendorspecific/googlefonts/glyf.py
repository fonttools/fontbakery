from fontbakery.prelude import check, disable, FAIL, Message


# Disabling this check since the previous implementation was
# bogus due to the way fonttools encodes the data into the TTF
# files and the new attempt at targetting the real problem is
# still not quite right.
# FIXME: reimplement this addressing the actual root cause of the issue.
# See also ongoing discussion at:
# https://github.com/fonttools/fontbakery/issues/1727
@disable
@check(
    id="googlefonts/negative_advance_width",
    rationale="""
        Advance width values in the Horizontal Metrics (htmx) table cannot be negative
        since they are encoded as unsigned 16-bit values. But some programs may infer
        and report a negative advance by looking up the x-coordinates of the glyphs
        directly on the glyf table.

        There are reports of broken versions of Glyphs.app causing this kind of problem
        as reported at [1] and [2].

        This check detects and reports such malformed glyf table entries.


        [1] https://github.com/fonttools/fontbakery/issues/1720

        [2] https://github.com/fonttools/fonttools/pull/1198
    """,
    conditions=["is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/issues/1720",
)
def check_negative_advance_width(ttFont):
    """Check that advance widths cannot be inferred as negative."""
    for glyphName in ttFont["glyf"].glyphs:
        coords = ttFont["glyf"][glyphName].coordinates
        rightX = coords[-3][0]
        leftX = coords[-4][0]
        advwidth = rightX - leftX
        if advwidth < 0:
            yield FAIL, Message(
                "bad-coordinates",
                f'Glyph "{glyphName}" has bad coordinates on the glyf'
                f" table, which may lead to the advance width to be"
                f" interpreted as a negative value ({advwidth}).",
            )
