from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/subsets_order",
    conditions=["family_metadata"],
    rationale="""
        The subsets listed in the METADATA.pb file should be sorted in
        alphabetical order.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_subsets_order(family_metadata):
    """METADATA.pb subsets should be alphabetically ordered."""
    expected = list(sorted(family_metadata.subsets))

    if list(family_metadata.subsets) != expected:
        subsets = "', '".join(family_metadata.subsets)
        expected = "', '".join(expected)
        yield FAIL, Message(
            "not-sorted",
            f"METADATA.pb subsets are not sorted in alphabetical order:"
            f" Got ['{subsets}'] and expected ['{expected}']",
        )
