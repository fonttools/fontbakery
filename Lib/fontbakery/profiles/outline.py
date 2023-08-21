import math

from beziers.path import BezierPath

from fontbakery.callable import condition, check
from fontbakery.status import PASS, WARN
from fontbakery.section import Section
from fontbakery.message import Message
from fontbakery.utils import bullet_list

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory  # noqa:F401 pylint:disable=W0611

ALIGNMENT_MISS_EPSILON = 2  # Two point lee-way on alignment misses
SHORT_PATH_EPSILON = 0.006  # <0.6% of total outline length makes a short segment
SHORT_PATH_ABSOLUTE_EPSILON = 3  # 3 units is a small outline
COLINEAR_EPSILON = 0.1  # Radians
JAG_AREA_EPSILON = 0.05  # <5% of total outline area makes a jaggy segment
JAG_ANGLE = 0.25  # Radians
FALSE_POSITIVE_CUTOFF = 100  # More than this and we don't make a report


@condition
def outlines_dict(ttFont):
    cmap = ttFont["cmap"].getBestCmap()
    return {
        (codepoint, glyphname): BezierPath.fromFonttoolsGlyph(ttFont, glyphname)
        for codepoint, glyphname in cmap.items()
    }


def close_but_not_on(yExpected, yTrue, tolerance):
    if yExpected == yTrue:
        return False
    if abs(yExpected - yTrue) <= tolerance:
        return True
    return False


@check(
    id="com.google.fonts/check/outline_alignment_miss",
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
def com_google_fonts_check_outline_alignment_miss(ttFont, outlines_dict, config):
    """Are there any misaligned on-curve points?"""
    alignments = {
        "baseline": 0,
        "x-height": ttFont["OS/2"].sxHeight,
        "cap-height": ttFont["OS/2"].sCapHeight,
        "ascender": ttFont["OS/2"].sTypoAscender,
        "descender": ttFont["OS/2"].sTypoDescender,
    }
    warnings = []
    for glyph, outlines in outlines_dict.items():
        codepoint, glyphname = glyph
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
                            f"{glyphname} (U+{codepoint:04X}):"
                            f" X={node.x},Y={node.y}"
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


@check(
    id="com.google.fonts/check/outline_short_segments",
    rationale=f"""
        This check looks for outline segments which seem particularly short (less
        than {SHORT_PATH_EPSILON:.1%} of the overall path length).

        This check is not run for variable fonts, as they may legitimately have
        short segments. As this check is liable to generate significant numbers
        of false positives, it will pass if there are more than
        {FALSE_POSITIVE_CUTOFF} reported short segments.
    """,
    conditions=["outlines_dict", "not is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3088",
)
def com_google_fonts_check_outline_short_segments(ttFont, outlines_dict, config):
    """Are any segments inordinately short?"""
    warnings = []
    for glyph, outlines in outlines_dict.items():
        codepoint, glyphname = glyph
        for p in outlines:
            outline_length = p.length
            segments = p.asSegments()
            if not segments:
                continue
            prev_was_line = len(segments[-1]) == 2
            for seg in p.asSegments():
                if math.isclose(seg.length, 0):  # That's definitely wrong
                    warnings.append(
                        f"{glyphname} (U+{codepoint:04X})"
                        f" contains a short segment {seg}"
                    )
                elif (
                    seg.length < SHORT_PATH_ABSOLUTE_EPSILON
                    or seg.length < SHORT_PATH_EPSILON * outline_length
                ) and (prev_was_line or len(seg) > 2):
                    warnings.append(
                        f"{glyphname} (U+{codepoint:04X})"
                        f" contains a short segment {seg}"
                    )
                prev_was_line = len(seg) == 2
        if len(warnings) > FALSE_POSITIVE_CUTOFF:
            yield PASS, (
                "So many short segments were found that this was probably by design."
            )
            return

    if warnings:
        formatted_list = bullet_list(config, warnings, bullet="*")
        yield WARN, Message(
            "found-short-segments",
            f"The following glyphs have segments which seem very short:\n\n"
            f"{formatted_list}",
        )
    else:
        yield PASS, "No short segments were found."


@check(
    id="com.google.fonts/check/outline_colinear_vectors",
    rationale="""
        This check looks for consecutive line segments which have the same angle. This
        normally happens if an outline point has been added by accident.

        This check is not run for variable fonts, as they may legitimately have
        colinear vectors.
    """,
    conditions=["outlines_dict", "not is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3088",
)
def com_google_fonts_check_outline_colinear_vectors(ttFont, outlines_dict, config):
    """Do any segments have colinear vectors?"""
    warnings = []
    for glyph, outlines in outlines_dict.items():
        codepoint, glyphname = glyph
        for p in outlines:
            segments = p.asSegments()
            if not segments:
                continue
            for i in range(0, len(segments)):
                prev = segments[i - 1]
                this = segments[i]
                if len(prev) == 2 and len(this) == 2:
                    if (
                        abs(prev.tangentAtTime(0).angle - this.tangentAtTime(0).angle)
                        < COLINEAR_EPSILON
                    ):
                        warnings.append(
                            f"{glyphname} (U+{codepoint:04X}):" f" {prev} -> {this}"
                        )
        if len(warnings) > FALSE_POSITIVE_CUTOFF:
            yield PASS, (
                "So many colinear vectors were found"
                " that this was probably by design."
            )
            return

    if warnings:
        formatted_list = bullet_list(config, sorted(set(warnings)), bullet="*")
        yield WARN, Message(
            "found-colinear-vectors",
            f"The following glyphs have colinear vectors:\n\n" f"{formatted_list}",
        )
    else:
        yield PASS, "No colinear vectors found."


@check(
    id="com.google.fonts/check/outline_jaggy_segments",
    rationale="""
        This check heuristically detects outline segments which form a particularly
        small angle, indicative of an outline error. This may cause false positives
        in cases such as extreme ink traps, so should be regarded as advisory and
        backed up by manual inspection.
    """,
    conditions=["outlines_dict", "not is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3064",
)
def com_google_fonts_check_outline_jaggy_segments(ttFont, outlines_dict, config):
    """Do outlines contain any jaggy segments?"""
    warnings = []
    for glyph, outlines in outlines_dict.items():
        codepoint, glyphname = glyph
        for p in outlines:
            segments = p.asSegments()
            if not segments:
                continue
            for i in range(0, len(segments)):
                prev = segments[i - 1]
                this = segments[i]
                in_vector = prev.tangentAtTime(1) * -1
                out_vector = this.tangentAtTime(0)
                if not (in_vector.magnitude * out_vector.magnitude):
                    continue
                angle = (in_vector @ out_vector) / (
                    in_vector.magnitude * out_vector.magnitude
                )
                if not (-1 <= angle <= 1):
                    continue
                jag_angle = math.acos(angle)
                if abs(jag_angle) > JAG_ANGLE or jag_angle == 0:
                    continue
                warnings.append(
                    f"{glyphname} (U+{codepoint:04X}):"
                    f" {prev}/{this} = {math.degrees(jag_angle)}"
                )

    if warnings:
        formatted_list = bullet_list(config, sorted(warnings), bullet="*")
        yield WARN, Message(
            "found-jaggy-segments",
            f"The following glyphs have jaggy segments:\n\n" f"{formatted_list}",
        )
    else:
        yield PASS, "No jaggy segments found."


@check(
    id="com.google.fonts/check/outline_semi_vertical",
    rationale="""
        This check detects line segments which are nearly, but not quite, exactly
        horizontal or vertical. Sometimes such lines are created by design, but often
        they are indicative of a design error.

        This check is disabled for italic styles, which often contain nearly-upright
        lines.
    """,
    conditions=["outlines_dict", "not is_variable_font", "not is_italic"],
    proposal="https://github.com/fonttools/fontbakery/pull/3088",
)
def com_google_fonts_check_outline_semi_vertical(ttFont, outlines_dict, config):
    """Do outlines contain any semi-vertical or semi-horizontal lines?"""
    warnings = []
    for glyph, outlines in outlines_dict.items():
        codepoint, glyphname = glyph
        for p in outlines:
            segments = p.asSegments()
            if not segments:
                continue
            for s in segments:
                if len(s) != 2:
                    continue
                angle = math.degrees((s.end - s.start).angle)
                for yExpected in [-180, -90, 0, 90, 180]:
                    if close_but_not_on(angle, yExpected, 0.5):
                        warnings.append(f"{glyphname} (U+{codepoint:04X}): {s}")

    if warnings:
        formatted_list = bullet_list(config, sorted(warnings), bullet="*")
        yield WARN, Message(
            "found-semi-vertical",
            f"The following glyphs have"
            f" semi-vertical/semi-horizontal lines:\n"
            f"\n"
            f"{formatted_list}",
        )
    else:
        yield PASS, "No semi-horizontal/semi-vertical lines found."


OUTLINE_PROFILE_IMPORTS = (
    ".",
    ("shared_conditions",),
)
profile_imports = (OUTLINE_PROFILE_IMPORTS,)
profile = profile_factory(default_section=Section("Outline Correctness Checks"))
OUTLINE_PROFILE_CHECKS = [
    "com.google.fonts/check/outline_alignment_miss",
    "com.google.fonts/check/outline_short_segments",
    "com.google.fonts/check/outline_colinear_vectors",
    "com.google.fonts/check/outline_jaggy_segments",
    "com.google.fonts/check/outline_semi_vertical",
]

profile.auto_register(globals())
profile.test_expected_checks(OUTLINE_PROFILE_CHECKS, exclusive=True)
