from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import bullet_list


@check(
    id="googlefonts/family/equal_codepoint_coverage",
    conditions=["are_ttf", "stylenames_are_canonical"],
    rationale="""
        For a given family, all fonts must have the same codepoint coverage.
        This is because we want to avoid the situation where, for example,
        a character is present in a regular font but missing in the italic style;
        turning on italic would cause the character to be rendered either as a
        fake italic (auto-slanted) or to show tofu.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4180",
)
def check_family_equal_codepoint_coverage(fonts, config):
    """Fonts have equal codepoint coverage"""
    cmaps = {}
    for font in fonts:
        stylename = font.canonical_stylename
        cmaps[stylename] = font.font_codepoints
    cmap_list = list(cmaps.values())
    common_cps = cmap_list[0].intersection(*cmap_list[1:])
    problems = []

    for style, cmap in cmaps.items():
        residue = cmap - common_cps
        if residue:
            problems.append(
                f"* {style} contains encoded codepoints not found"
                " in other related fonts:"
                + bullet_list(config, ["U+%04x" % cp for cp in residue])
            )

    if problems:
        problems = "\n".join(problems)
        yield FAIL, Message("glyphset-diverges", problems)
