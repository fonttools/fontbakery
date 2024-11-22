from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/empty_designer",
    rationale="""
        Any font published on Google Fonts must credit one or several authors,
        foundry and/or individuals.

        Ideally, all authors listed in the upstream repository's AUTHORS.txt should
        be mentioned in the designer field.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3961",
)
def check_metadata_empty_designer(family_metadata):
    """At least one designer is declared in METADATA.pb"""

    if family_metadata.designer.strip() == "":
        yield FAIL, Message("empty-designer", "Font designer field is empty.")

    # TODO: Parse AUTHORS.txt and WARN if names do not match
    # (and then maybe rename the check-id)
