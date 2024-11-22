from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/metadata/category_hints",
    rationale="""
        Sometimes the font familyname contains words that hint at which is the most
        likely correct category to be declared on METADATA.pb
    """,
    conditions=["family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3624",
)
def check_metadata_category_hint(family_metadata):
    """
    Check if category on METADATA.pb matches what can be inferred from the family name.
    """

    HINTS = {
        "SANS_SERIF": ["Sans", "Grotesk", "Grotesque"],
        "SERIF": ["Old Style", "Transitional", "Garamond", "Serif", "Slab"],
        "DISPLAY": ["Display"],
        "HANDWRITING": ["Hand", "Script"],
    }

    inferred_category = None
    for category, hints in HINTS.items():
        for hint in hints:
            if hint in family_metadata.name:
                inferred_category = category
                break

    if (
        inferred_category is not None
        and inferred_category not in family_metadata.category
    ):
        yield WARN, Message(
            "inferred-category",
            f'Familyname seems to hint at "{inferred_category}" but'
            f' METADATA.pb declares it as "{family_metadata.category}".',
        )
