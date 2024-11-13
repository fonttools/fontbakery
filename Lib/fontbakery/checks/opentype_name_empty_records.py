from fontbakery.prelude import check, FAIL, Message


@check(
    id="opentype/name/empty_records",
    rationale="""
        Check the name table for empty records,
        as this can cause problems in Adobe apps.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2369",
)
def check_name_empty_records(ttFont):
    """Check name table for empty records."""
    for name_record in ttFont["name"].names:
        name_string = name_record.toUnicode().strip()
        if len(name_string) == 0:
            name_key = tuple(
                [
                    name_record.platformID,
                    name_record.platEncID,
                    name_record.langID,
                    name_record.nameID,
                ]
            )
            yield FAIL, Message(
                "empty-record",
                f'"name" table record with key={name_key} is'
                f" empty and should be removed.",
            )
