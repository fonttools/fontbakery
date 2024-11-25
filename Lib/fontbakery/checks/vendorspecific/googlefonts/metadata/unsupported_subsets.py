from fontbakery.prelude import FAIL, Message, check
from fontbakery.utils import exit_with_install_instructions


@check(
    id="googlefonts/metadata/unsupported_subsets",
    rationale="""
        This check ensures that the subsets specified on a METADATA.pb file are
        actually supported (even if only partially) by the font files.

        Subsets for which none of the codepoints are supported will cause the
        check to FAIL.
    """,
    conditions=["family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3533",
    severity=10,  # max severity because this blocks font pushes to production.
)
def check_metadata_unsupported_subsets(family_metadata, ttFont, font_codepoints):
    """Check for METADATA subsets with zero support."""
    try:
        from gfsubsets import CodepointsInSubset, ListSubsets
    except ImportError:
        exit_with_install_instructions("googlefonts")

    for subset in family_metadata.subsets:
        if subset == "menu":
            continue

        if subset not in ListSubsets():
            yield FAIL, Message(
                "unknown-subset",
                f"Please remove the unrecognized subset '{subset}'"
                f" from the METADATA.pb file.",
            )
            continue

        subset_codepoints = CodepointsInSubset(subset, unique_glyphs=True)
        # All subsets now have these magic codepoints
        subset_codepoints -= set([0, 13, 32, 160])

        if len(subset_codepoints.intersection(font_codepoints)) == 0:
            yield FAIL, Message(
                "unsupported-subset",
                f"Please remove '{subset}' from METADATA.pb since none"
                f" of its glyphs are supported by this font file.",
            )
