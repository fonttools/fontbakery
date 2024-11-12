from fontbakery.prelude import check, Message, FAIL


@check(
    id="fvar_name_entries",
    conditions=["is_variable_font"],
    rationale="""
        The purpose of this check is to make sure that all name entries referenced
        by variable font instances do exist in the name table.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2069",
)
def check_fvar_name_entries(ttFont):
    """All name entries referenced by fvar instances exist on the name table?"""

    for instance in ttFont["fvar"].instances:
        entries = [
            entry
            for entry in ttFont["name"].names
            if entry.nameID == instance.subfamilyNameID
        ]
        if len(entries) == 0:
            yield FAIL, Message(
                "missing-name",
                f"Named instance with coordinates {instance.coordinates}"
                f" lacks an entry on the name table"
                f" (nameID={instance.subfamilyNameID}).",
            )
