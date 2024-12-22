import math
from copy import deepcopy

from beziers.path import BezierPath, Line, Point
from fontTools.pens.boundsPen import BoundsPen

from fontbakery.prelude import check, Message, FAIL, PASS, WARN


def x_leftmost_intersection(paths, xMax, xMin, y):
    for y_adjust in range(0, 20, 2):
        line = Line(Point(xMin - 100, y + y_adjust), Point(xMax + 100, y + y_adjust))
        for path in paths:
            for s in path.asSegments():
                intersections = s.intersections(line)
                if intersections:
                    return intersections[0].point.x


@check(
    id="opentype/italic_angle",
    conditions=["style"],
    rationale="""
        The 'post' table italicAngle property should be a reasonable amount, likely
        not more than 30°. Note that in the OpenType specification, the value is
        negative for a rightward lean.

        https://docs.microsoft.com/en-us/typography/opentype/spec/post
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_italic_angle(ttFont, style):
    """Checking post.italicAngle value."""

    # This check modifies the font file with `.draw(boundspen)`
    # so here we'll work with a copy of the object so that we
    # do not affect other checks:
    ttFont_copy = deepcopy(ttFont)

    value = ttFont_copy["post"].italicAngle
    glyphset = ttFont_copy.getGlyphSet()
    bad_glyphs = []
    calculated_italic_angle = None
    for glyph_name in (
        "bar",
        "uni007C",  # VERTICAL LINE
        "bracketleft",
        "uni005B",  # LEFT SQUARE BRACKET
        "H",
        "uni0048",  # LATIN CAPITAL LETTER H
        "I",
        "uni0049",  # LATIN CAPITAL LETTER I
    ):
        if glyph_name not in glyphset:
            continue

        # Get bounds
        boundspen = BoundsPen(glyphset)
        glyphset[glyph_name].draw(boundspen)
        bounds = boundspen.bounds
        if not bounds:
            bad_glyphs.append(glyph_name)
            continue

        # Calculating italic angle from the font's glyph outlines
        paths = BezierPath.fromFonttoolsGlyph(ttFont_copy, glyph_name)
        (xMin, yMin, xMax, yMax) = bounds

        # Measure at 20% distance from bottom and top
        y_bottom = yMin + (yMax - yMin) * 0.2
        y_top = yMin + (yMax - yMin) * 0.8
        x_intsctn_bottom = x_leftmost_intersection(paths, xMax, xMin, y_bottom)
        x_intsctn_top = x_leftmost_intersection(paths, xMax, xMin, y_top)

        # Fails to calculate the intersection for some situations,
        # so try again with next glyph
        if not x_intsctn_bottom or not x_intsctn_top:
            continue

        x_d = x_intsctn_top - x_intsctn_bottom
        y_d = y_top - y_bottom
        calculated_italic_angle = -1 * math.degrees(math.atan2(x_d, y_d))
        break

    passed = True
    # Wasn't able to calculate italic angle from the font's glyph outlines,
    # so revert to previous functionality of assuming a right-leaning Italic
    # and report a warning if italicAngle is positive
    if calculated_italic_angle is None:
        if value > 0:
            passed = False
            yield WARN, Message(
                "positive",
                (
                    "The value of post.italicAngle is positive, which"
                    " is likely a mistake and should become negative"
                    " for right-leaning Italics. If this font is"
                    " left-leaning, ignore this warning."
                ),
            )
    else:
        # Checking that italicAngle matches the calculated value
        # We allow a 0.1° tolerance
        if calculated_italic_angle < 0.1 and value > 0:
            passed = False
            yield WARN, Message(
                "positive",
                f"The value of post.italicAngle is positive, which"
                f" is likely a mistake and should become negative"
                f" for right-leaning Italics.\n"
                f"post.italicAngle: {value:.2f}\n"
                f"angle calculated from outlines:"
                f" {calculated_italic_angle:.2f})",
            )
        if calculated_italic_angle > 0.1 and value < 0:
            passed = False
            yield WARN, Message(
                "negative",
                f"The value of post.italicAngle is negative, which"
                f" is likely a mistake and should become positive"
                f" for left-leaning Italics.\n"
                f"post.italicAngle: {value:.2f}\n"
                f"angle calculated from outlines:"
                f" {calculated_italic_angle:.2f})",
            )

    # Checking that italicAngle > 90
    if abs(value) > 90:
        passed = False
        yield FAIL, Message(
            "over-90-degrees",
            (
                "The value of post.italicAngle is over 90°, which"
                " is surely a mistake."
            ),
        )

    # Checking that italicAngle is less than 20° (not good) or 30° (bad)
    # Also note we invert the value to check it in a clear way
    if abs(value) > 30:
        passed = False
        yield WARN, Message(
            "over-30-degrees",
            (
                f"The value of post.italicAngle ({value:.2f}) is very high"
                f" (over -30° or 30°) and should be confirmed."
            ),
        )
    elif abs(value) > 20:
        passed = False
        yield WARN, Message(
            "over-20-degrees",
            (
                f"The value of post.italicAngle ({value:.2f}) seems very high"
                f" (over -20° or 20°) and should be confirmed."
            ),
        )

    # Checking if italicAngle matches font style:
    if "Italic" in style:
        if ttFont_copy["post"].italicAngle == 0:
            passed = False
            yield FAIL, Message(
                "zero-italic",
                "Font is italic, so post.italicAngle should be non-zero.",
            )
    else:
        if ttFont_copy["post"].italicAngle != 0:
            passed = False
            yield FAIL, Message(
                "non-zero-upright",
                "Font is not italic, so post.italicAngle should be equal to zero.",
            )

    if bad_glyphs:
        passed = False
        yield WARN, Message(
            "empty-glyphs",
            (
                "The following glyphs were present but did not contain any outlines: "
                + ", ".join(bad_glyphs)
            ),
        )

    if passed:
        yield PASS, (f'Value of post.italicAngle is {value:.2f} with style="{style}".')
