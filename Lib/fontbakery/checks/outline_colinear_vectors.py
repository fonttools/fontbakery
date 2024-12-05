from fontbakery.prelude import check, Message, PASS, WARN
from fontbakery.utils import bullet_list
from fontbakery.checks.outline_settings import (
    COLINEAR_EPSILON,
    FALSE_POSITIVE_CUTOFF,
)


@check(
    id="outline_colinear_vectors",
    rationale="""
        This check looks for consecutive line segments which have the same angle. This
        normally happens if an outline point has been added by accident.

        This check is not run for variable fonts, as they may legitimately have
        colinear vectors.
    """,
    conditions=["outlines_dict", "not is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3088",
)
def check_outline_colinear_vectors(ttFont, outlines_dict, config):
    """Do any segments have colinear vectors?"""
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
                if len(prev) == 2 and len(this) == 2:
                    if (
                        abs(prev.tangentAtTime(0).angle - this.tangentAtTime(0).angle)
                        < COLINEAR_EPSILON
                    ):
                        warnings.append(f"{display_name}: {prev} -> {this}")
        if len(warnings) > FALSE_POSITIVE_CUTOFF:
            yield PASS, (
                "So many colinear vectors were found that this was probably by design."
            )
            return

    if warnings:
        formatted_list = bullet_list(config, sorted(set(warnings)), bullet="*")
        yield WARN, Message(
            "found-colinear-vectors",
            f"The following glyphs have colinear vectors:\n\n{formatted_list}",
        )
    else:
        yield PASS, "No colinear vectors found."
