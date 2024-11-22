from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/match_name_familyname",
    conditions=[
        "family_metadata",  # that's the family-wide metadata!
        "font_metadata",
    ],  # and this one's specific to a single file
    rationale="""
        This check ensures that the 'name' field in each font's entry in
        the METADATA.pb file matches the 'name' field at the top level of
        the METADATA.pb.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_match_name_familyname(family_metadata, font_metadata):
    """METADATA.pb: Check font name is the same as family name."""
    if font_metadata.name != family_metadata.name:
        yield FAIL, Message(
            "mismatch",
            f"METADATA.pb: {font_metadata.filename}:\n"
            f' Family name "{family_metadata.name}" does not match'
            f' font name: "{font_metadata.name}"',
        )
