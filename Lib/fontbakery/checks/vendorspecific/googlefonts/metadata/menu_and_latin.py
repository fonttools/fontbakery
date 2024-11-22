from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/menu_and_latin",
    conditions=["family_metadata"],
    rationale="""
        The 'menu' and 'latin' subsets are mandatory in METADATA.pb for the
        font to display correctly on the Google Fonts website.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/912#issuecomment-237935444",
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
    ],
)
def check_metadata_menu_and_latin(family_metadata):
    """METADATA.pb should contain at least "menu" and "latin" subsets."""
    missing = []
    for s in ["menu", "latin"]:
        if s not in list(family_metadata.subsets):
            missing.append(s)

    if missing:
        if len(missing) == 2:
            missing = "both"
        else:
            missing = f'"{missing[0]}"'

        yield FAIL, Message(
            "missing",
            f'Subsets "menu" and "latin" are mandatory,'
            f" but METADATA.pb is missing {missing}.",
        )
