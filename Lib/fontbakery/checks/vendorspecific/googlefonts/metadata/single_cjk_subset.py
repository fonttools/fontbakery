from fontbakery.prelude import check, Message, FATAL


@check(
    id="googlefonts/metadata/single_cjk_subset",
    conditions=["family_metadata"],
    rationale="""
        Check METADATA.pb file only contains a single CJK subset since the Google Fonts
        backend doesn't support multiple CJK subsets.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4779",
)
def check_metadata_single_cjk_subset(family_metadata):
    """Check METADATA.pb file only contains a single CJK subset."""
    cjk_subsets = frozenset(
        [
            "chinese-hongkong",
            "chinese-simplified",
            "chinese-traditional",
            "korean",
            "japanese",
        ]
    )
    cjk_subset_in_font = set(family_metadata.subsets) & cjk_subsets

    if len(cjk_subset_in_font) > 1:
        cjk_subsets = ", ".join(cjk_subsets)
        yield FATAL, Message(
            "multiple-cjk-subsets",
            "METADATA.pb file contains more than one CJK subset."
            f" Please choose only one from {cjk_subsets}.",
        )
