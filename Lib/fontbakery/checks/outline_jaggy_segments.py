import math

from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import bullet_list
from fontbakery.checks.outline_settings import JAG_ANGLE


@check(
    id="outline_jaggy_segments",
    rationale="""
        This check heuristically detects outline segments which form a particularly
        small angle, indicative of an outline error. This may cause false positives
        in cases such as extreme ink traps, so should be regarded as advisory and
        backed up by manual inspection.
    """,
    conditions=["outlines_dict", "not is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3064",
)
def check_outline_jaggy_segments(ttFont, outlines_dict, config):
    """Do outlines contain any jaggy segments?"""
    warnings = []

    for glyph, outlines in outlines_dict.items():
        glyphname, display_name = glyph
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
                    f"{display_name}: {prev}/{this} = {math.degrees(jag_angle)}"
                )

    if warnings:
        formatted_list = bullet_list(config, sorted(warnings), bullet="*")
        yield WARN, Message(
            "found-jaggy-segments",
            f"The following glyphs have jaggy segments:\n\n{formatted_list}",
        )
    else:
        yield PASS, "No jaggy segments found."
