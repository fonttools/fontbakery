from collections import defaultdict

from fontbakery.prelude import check, Message, WARN
from fontbakery.utils import bullet_list


@check(
    id="outline_direction",
    rationale="""
        In TrueType fonts, the outermost contour of a glyph should be oriented
        clockwise, while the inner contours should be oriented counter-clockwise.
        Getting the path direction wrong can lead to rendering issues in some
        software.
    """,
    conditions=["outlines_dict", "is_ttf"],
    proposal="https://github.com/fonttools/fontbakery/issues/2056",
)
def check_outline_direction(ttFont, outlines_dict, config):
    """Check the direction of the outermost contour in each glyph"""
    warnings = []

    def bounds_contains(bb1, bb2):
        return (
            bb1.left <= bb2.left
            and bb1.right >= bb2.right
            and bb1.top >= bb2.top
            and bb1.bottom <= bb2.bottom
        )

    for glyph, outlines in outlines_dict.items():
        glyphname, display_name = glyph
        # Find outlines which are not contained within another outline
        outline_bounds = [path.bounds() for path in outlines]
        is_within = defaultdict(list)
        for i, my_bounds in enumerate(outline_bounds):
            if my_bounds.bl is None:
                warnings.append(
                    f"{display_name} has a path with no bounds (probably a single point)"
                )
                continue
            for j in range(0, len(outline_bounds)):
                if i == j:
                    continue
                their_bounds = outline_bounds[j]
                if their_bounds.bl is None:
                    continue  # Already warned
                if bounds_contains(my_bounds, their_bounds):
                    is_within[j].append(i)
        # The outermost paths are those which are not within anything
        for i, path in enumerate(outlines):
            if is_within[i]:
                continue
            if path.direction == 1:
                warnings.append(f"{display_name} has a counter-clockwise outer contour")

    if warnings:
        formatted_list = bullet_list(config, sorted(warnings), bullet="*")
        yield WARN, Message(
            "ccw-outer-contour",
            f"The following glyphs have a counter-clockwise outer contour:\n\n"
            f"{formatted_list}",
        )
