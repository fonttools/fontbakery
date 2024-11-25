from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/description/min_length",
    conditions=["description"],
    rationale="""
        The DESCRIPTION.en_us.html file is intended to provide a brief overview of
        the font family. It should be long enough to be useful to users, but not so
        long that it becomes overwhelming.

        We chose 200 bytes as a minimum length because it suggests that someone has
        taken the time to write "something sensible" about the font.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_description_min_length(description):
    """DESCRIPTION.en_us.html must have more than 200 bytes."""
    if len(description) <= 200:
        yield FAIL, Message(
            "too-short",
            "DESCRIPTION.en_us.html must have size larger than 200 bytes.",
        )
