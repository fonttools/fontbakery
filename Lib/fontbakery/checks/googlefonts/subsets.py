from collections import defaultdict

from fontbakery.prelude import FAIL, WARN, Message, check
from fontbakery.utils import exit_with_install_instructions


@check(
    id="com.google.fonts/check/metadata/unsupported_subsets",
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
def com_google_fonts_check_metadata_unsupported_subsets(
    family_metadata, ttFont, font_codepoints
):
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


@check(
    id="com.google.fonts/check/metadata/unreachable_subsetting",
    rationale="""
        This check ensures that all encoded glyphs in the font are covered by a
        subset declared in the METADATA.pb. Google Fonts splits the font into
        a set of subset fonts based on the contents of the `subsets` field and
        the subset definitions in the `glyphsets` repository.

        Any encoded glyphs which are not by any of these subset definitions
        will not be served in the subsetted fonts, and so will be unreachable to
        the end user.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4097",
        "https://github.com/fonttools/fontbakery/pull/4273",
    ],
    severity=2,
)
def com_google_fonts_check_metadata_unreachable_subsetting(font, config):
    """Check for codepoints not covered by METADATA subsets."""
    try:
        import unicodedata2
        from gfsubsets import CodepointsInSubset, ListSubsets, SubsetsInFont
    except ImportError:
        exit_with_install_instructions("googlefonts")

    from fontbakery.utils import pretty_print_list

    # Use the METADATA.pb subsets if we have them
    if font.metadata_file:
        metadata = font.family_metadata
        if metadata:
            subsets = metadata.subsets
        else:
            yield FAIL, Message(
                "unparsable-metadata", "Could not parse metadata.pb file"
            )
            return
    else:
        # Follow what the packager would do
        subsets = [s[0] for s in SubsetsInFont(font.file, 50, 0.01)]

    font_codepoints = font.font_codepoints
    for subset in subsets:
        font_codepoints = font_codepoints - set(CodepointsInSubset(subset))

    if not font_codepoints:
        # it is all fine!
        return

    unreachable = []
    subsets_for_cps = defaultdict(set)
    # This is faster than calling SubsetsForCodepoint for each codepoint
    for subset in ListSubsets():
        cps = CodepointsInSubset(subset, unique_glyphs=True)
        for cp in cps or []:
            subsets_for_cps[cp].add(subset)

    for codepoint in sorted(font_codepoints):
        subsets_for_cp = subsets_for_cps[codepoint]

        if len(subsets_for_cp) == 0:
            message = "not included in any glyphset definition"
        elif len(subsets_for_cp) == 1:
            message = "try adding " + ", ".join(subsets_for_cp)
        else:
            message = "try adding one of: " + ", ".join(subsets_for_cp)

        try:
            name = unicodedata2.name(chr(codepoint))
        except Exception:
            name = ""

        unreachable.append(" * U+%04X %s: %s" % (codepoint, name, message))

    message = """The following codepoints supported by the font are not covered by
    any subsets defined in the font's metadata file, and will never
    be served. You can solve this by either manually adding additional
    subset declarations to METADATA.pb, or by editing the glyphset
    definitions.\n\n"""

    subsets = ", ".join(f"`{s}`" for s in subsets)
    message += pretty_print_list(config, unreachable, sep="\n", glue="\n")
    message += (
        f"\n\nOr you can add the above codepoints to one"
        f" of the subsets supported by the font: {subsets}"
    )

    yield WARN, Message("unreachable-subsetting", message)
