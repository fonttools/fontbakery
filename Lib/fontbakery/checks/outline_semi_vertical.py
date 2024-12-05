import math

from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import bullet_list


@check(
    id="outline_semi_vertical",
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
def check_outline_semi_vertical(ttFont, outlines_dict, config):
    """Do outlines contain any semi-vertical or semi-horizontal lines?"""
    from fontbakery.utils import close_but_not_on

    warnings = []

    for glyph, outlines in outlines_dict.items():
        glyphname, display_name = glyph
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
                        warnings.append(f"{display_name}: {s}")

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
