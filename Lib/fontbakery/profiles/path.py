from beziers.path import BezierPath

from fontbakery.fonts_profile import (
    profile_factory,
)  # NOQA pylint: disable=unused-import
from fontbakery.callable import condition, check
from fontbakery.checkrunner import FAIL, PASS, WARN, Section
from fontbakery.message import Message
from fontbakery.utils import pretty_print_list
import math


ALIGNMENT_MISS_EPSILON = 2  # Two point lee-way on alignment misses
SHORT_PATH_EPSILON = 0.006  # <0.6% of total path length makes a short segment
SHORT_PATH_ABSOLUTE_EPSILON = 3  # 3 units is a small path
COLINEAR_EPISON = 0.1  # Radians
JAG_AREA_EPSILON = 0.05  # <5% of total path area makes a jaggy segment
JAG_ANGLE = 0.25  # Radians


@condition
def paths_dict(ttFont):
    return {g: BezierPath.fromFonttoolsGlyph(ttFont, g) for g in ttFont.getGlyphOrder()}


def close_but_not_on(yExpected, yTrue, tolerance):
    if yExpected == yTrue:
        return False
    if abs(yExpected - yTrue) <= tolerance:
        return True
    return False


@check(id="com.google.fonts/check/path_alignment_miss", conditions=["paths_dict"])
def com_google_fonts_check_path_alignment_miss(ttFont, paths_dict):
    """Are there any misaligned on-curve points?"""
    alignments = {
        "baseline": 0,
        "x-height": ttFont["OS/2"].sxHeight,
        "cap-height": ttFont["OS/2"].sCapHeight,
        "ascender": ttFont["OS/2"].sTypoAscender,
        "descender": ttFont["OS/2"].sTypoDescender,
    }
    warnings = []
    for glyphname, paths in paths_dict.items():
        for p in paths:
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
                            f"{glyphname}: X={node.x},Y={node.y} (should be at {line} {yExpected}?)"
                        )

    if warnings:
        formatted_list = "\t* " + pretty_print_list(warnings, sep="\n\t* ")
        yield WARN, Message(
            "found-misalignments",
            f"The following glyphs have on-curve points which"
            f" have potentially incorrect y coordinates:\n"
            f"{formatted_list}",
        )
    else:
        yield PASS, ("Y-coordinates of points fell on appropriate boundaries.")


@check(
    id="com.google.fonts/check/path_short_segments",
    conditions=["paths_dict", "is_not_variable_font"],
)
def com_google_fonts_check_path_short_segments(ttFont, paths_dict):
    """Are any segments inordinately short?"""
    warnings = []
    for glyphname, paths in paths_dict.items():
        for p in paths:
            path_length = p.length
            segments = p.asSegments()
            if not segments:
                continue
            prev_was_line = len(segments[-1]) == 2
            for seg in p.asSegments():
                if (
                    seg.length < SHORT_PATH_ABSOLUTE_EPSILON
                    or seg.length < SHORT_PATH_EPSILON * path_length
                ) and (prev_was_line or len(seg) > 2):
                    warnings.append(f"{glyphname} contains a short segment {seg}")
                prev_was_line = len(seg) == 2
    if warnings:
        formatted_list = "\t* " + pretty_print_list(warnings, sep="\n\t* ")
        yield WARN, Message(
            "found-short-segments",
            f"The following glyphs have segments which seem very short:\n"
            f"{formatted_list}",
        )
    else:
        yield PASS, ("No short segments were found.")


@check(
    id="com.google.fonts/check/path_colinear_vectors",
    conditions=["paths_dict", "is_not_variable_font"],
)
def com_google_fonts_check_path_colinear_vectors(ttFont, paths_dict):
    """Do any segments have colinear vectors?"""
    warnings = []
    for glyphname, paths in paths_dict.items():
        for p in paths:
            segments = p.asSegments()
            if not segments:
                continue
            for i in range(0, len(segments)):
                prev = segments[i - 1]
                this = segments[i]
                if len(prev) == 2 and len(this) == 2:
                    if (
                        abs(prev.tangentAtTime(0).angle - this.tangentAtTime(0).angle)
                        < COLINEAR_EPISON
                    ):
                        warnings.append(glyphname)

    if warnings:
        formatted_list = "\t* " + pretty_print_list(list(set(warnings)), sep="\n\t* ")
        yield WARN, Message(
            "found-colinear-vectors",
            f"The following glyphs have colinear vectors:\n" f"{formatted_list}",
        )
    else:
        yield PASS, ("No colinear vectors found.")


@check(
    id="com.google.fonts/check/path_jaggy_segments",
    conditions=["paths_dict", "is_not_variable_font"],
)
def com_google_fonts_check_path_jaggy_segments(ttFont, paths_dict):
    """Do paths contain any jaggy segments?"""
    warnings = []
    for glyphname, paths in paths_dict.items():
        for p in paths:
            segments = p.asSegments()
            path_area = None
            if not segments:
                continue
            for i in range(0, len(segments)):
                prev = segments[i - 1]
                this = segments[i]
                jag_angle = math.acos(
                    ((prev.start - prev.end) @ (this.end - this.start))
                    / (
                        (prev.start - prev.end).magnitude
                        * (this.end - this.start).magnitude
                    )
                )
                if abs(jag_angle) > JAG_ANGLE:
                    continue
                jag_area = (
                    ((prev.start.x * prev.end.y) - (prev.start.y * prev.end.x))
                    + ((this.start.x * this.end.y) - (this.start.y * this.end.x))
                    + ((prev.start.x * this.end.y) - (prev.start.y * this.end.x))
                )
                if jag_area < JAG_AREA_EPSILON * p.area:
                    warnings.append(f"{glyphname}: {prev}/{this}")

    if warnings:
        formatted_list = "\t* " + pretty_print_list(list(set(warnings)), sep="\n\t* ")
        yield WARN, Message(
            "found-jaggy-segments",
            f"The following glyphs have jaggy segments:\n" f"{formatted_list}",
        )
    else:
        yield PASS, ("No jaggy segments found.")


@check(
    id="com.google.fonts/check/path_semi_vertical",
    conditions=["paths_dict", "is_not_variable_font"],
)
def com_google_fonts_check_path_semi_vertical(ttFont, paths_dict):
    """Do paths contain any semi-vertical or semi-horizontal lines?"""
    warnings = []
    for glyphname, paths in paths_dict.items():
        for p in paths:
            segments = p.asSegments()
            path_area = None
            if not segments:
                continue
            for s in segments:
                if len(s) != 2:
                    continue
                angle = math.degrees((s.end - s.start).angle)
                for yExpected in [-180, -90, 0, 90, 180]:
                    if close_but_not_on(angle, yExpected, 0.5):
                        warnings.append(f"{glyphname}: {s}")

    if warnings:
        formatted_list = "\t* " + pretty_print_list(list(set(warnings)), sep="\n\t* ")
        yield WARN, Message(
            "found-semi-vertical",
            f"The following glyphs have semi-vertical/semi-horizontal lines:\n"
            f"{formatted_list}",
        )
    else:
        yield PASS, ("No jaggy segments found.")


PATH_PROFILE_IMPORTS = (
    ".",
    ("shared_conditions",),
)
profile_imports = (PATH_PROFILE_IMPORTS,)
profile = profile_factory(default_section=Section("Path Correctness Checks"))
PATH_PROFILE_CHECKS = [
    "com.google.fonts/check/path_alignment_miss",
    "com.google.fonts/check/path_short_segments",
    "com.google.fonts/check/path_colinear_vectors",
    "com.google.fonts/check/path_jaggy_segments",
    "com.google.fonts/check/path_semi_vertical",
]

profile.auto_register(globals())
profile.test_expected_checks(PATH_PROFILE_CHECKS, exclusive=True)
