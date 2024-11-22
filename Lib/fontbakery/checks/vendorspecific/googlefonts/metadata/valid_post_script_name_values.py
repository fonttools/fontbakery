from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/valid_post_script_name_values",
    conditions=["font_metadata", "font_familynames"],
    rationale="""
        Ensures that the postscript name in METADATA.pb contains the font's
        family name (with no spaces) as detected from the font binary.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_valid_post_script_name_values(font_metadata, font_familynames):
    """METADATA.pb font.post_script_name field contains font name in right format?"""
    possible_psnames = [
        "".join(str(font_familyname).split()) for font_familyname in font_familynames
    ]
    metadata_psname = "".join(font_metadata.post_script_name.split("-"))
    if not any(psname in metadata_psname for psname in possible_psnames):
        possible_psnames = ", ".join(possible_psnames)
        yield FAIL, Message(
            "mismatch",
            f"METADATA.pb"
            f' postScriptName ("{font_metadata.post_script_name}")'
            f' does not match correct font name format ("{possible_psnames}").',
        )
