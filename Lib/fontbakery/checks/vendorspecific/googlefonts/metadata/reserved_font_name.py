from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/metadata/reserved_font_name",
    conditions=["font_metadata", "not rfn_exception"],
    rationale="""
        Unless an exception has been granted, we expect fonts on
        Google Fonts not to use the "Reserved Font Name" clause in their
        copyright information. This is because fonts with RFNs are difficult
        to modify in a libre ecosystem; anyone who forks the font (with a
        view to changing it) must first rename the font, which makes
        it difficult to pass changes back to upstream.

        There is also a potential licensing difficulty, in that Google Fonts
        web service subsets the font - a modification of the original - but
        then delivers the font with the same name, which could be seen as a
        violation of the reserved font name clause.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_reserved_font_name(font_metadata):
    """Copyright notice on METADATA.pb should not contain 'Reserved Font Name'."""
    if "Reserved Font Name" in font_metadata.copyright:
        yield WARN, Message(
            "rfn",
            f"METADATA.pb:"
            f' copyright field ("{font_metadata.copyright}")'
            f' contains "Reserved Font Name".'
            f" This is an error except in a few specific rare cases.",
        )
