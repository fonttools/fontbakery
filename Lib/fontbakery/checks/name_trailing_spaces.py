from fontbakery.prelude import check, Message, PASS, FAIL


@check(
    id="name/trailing_spaces",
    proposal="https://github.com/fonttools/fontbakery/issues/2417",
    rationale="""
        This check ensures that no entries in the name table end in
        spaces; trailing spaces, particularly in font names, can be
        confusing to users. In most cases this can be fixed by
        removing trailing spaces from the metadata fields in the font
        editor.
    """,
)
def check_name_trailing_spaces(ttFont):
    """Name table records must not have trailing spaces."""
    failed = False
    for name_record in ttFont["name"].names:
        name_string = name_record.toUnicode()
        if name_string != name_string.strip():
            failed = True
            name_key = tuple(
                [
                    name_record.platformID,
                    name_record.platEncID,
                    name_record.langID,
                    name_record.nameID,
                ]
            )
            shortened_str = name_record.toUnicode()
            if len(shortened_str) > 25:
                shortened_str = shortened_str[:10] + "[...]" + shortened_str[-10:]
            yield FAIL, Message(
                "trailing-space",
                f"Name table record with key = {name_key} has trailing spaces"
                f" that must be removed: '{shortened_str}'",
            )
    if not failed:
        yield PASS, "No trailing spaces on name table entries."
