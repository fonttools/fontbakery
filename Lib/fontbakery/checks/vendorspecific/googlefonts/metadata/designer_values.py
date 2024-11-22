from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/designer_values",
    conditions=["family_metadata"],
    rationale="""
        We must use commas instead of forward slashes because the server-side code
        at the fonts.google.com directory will segment the string on the commas into
        a list of names and display the first item in the list as the
        "principal designer" while the remaining names are identified as "contributors".

        See eg https://fonts.google.com/specimen/Rubik
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2479",
)
def check_metadata_designer_values(family_metadata):
    """Multiple values in font designer field in
    METADATA.pb must be separated by commas."""

    if "/" in family_metadata.designer:
        yield FAIL, Message(
            "slash",
            f"Font designer field contains a forward slash"
            f" '{family_metadata.designer}'."
            f" Please use commas to separate multiple names instead.",
        )
