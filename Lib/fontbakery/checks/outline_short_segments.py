import math

from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import bullet_list
from fontbakery.checks.outline_settings import (
    FALSE_POSITIVE_CUTOFF,
    SHORT_PATH_ABSOLUTE_EPSILON,
    SHORT_PATH_EPSILON,
)


@check(
    id="outline_short_segments",
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
def check_outline_short_segments(ttFont, outlines_dict, config):
    """Are any segments inordinately short?"""
    warnings = []

    for glyph, outlines in outlines_dict.items():
        glyphname, display_name = glyph
        for p in outlines:
            outline_length = p.length
            segments = p.asSegments()
            if not segments:
                continue
            prev_was_line = len(segments[-1]) == 2
            for seg in p.asSegments():
                if math.isclose(seg.length, 0):  # That's definitely wrong
                    warnings.append(f"{display_name} contains a short segment {seg}")
                elif (
                    seg.length < SHORT_PATH_ABSOLUTE_EPSILON
                    or seg.length < SHORT_PATH_EPSILON * outline_length
                ) and (prev_was_line or len(seg) > 2):
                    warnings.append(f"{display_name} contains a short segment {seg}")
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
