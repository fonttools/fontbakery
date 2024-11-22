from fontbakery.prelude import check, Message, FATAL


@check(
    id="googlefonts/metadata/date_added",
    conditions=["family_metadata"],
    rationale="""
        The date_added field must not be empty or malformed.

        Expected format is "YYYY-MM-DD"
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4729",
)
def check_metadata_date_added(family_metadata):
    """Validate 'date_added' field on METADATA.pb."""

    if not family_metadata.date_added or family_metadata.date_added == "":
        yield FATAL, Message("empty", "The date_added field is missing or is empty")

    else:
        elements = family_metadata.date_added.split("-")
        if not (
            len(elements) == 3  # year, month and day
            and len(elements[0]) == 4  #  4 digit year
            and len(elements[1]) == 2  #  2 digit month
            and len(elements[2]) == 2  #  2 digit day
            and int(elements[0]) is not None  # year must be a number
            and int(elements[1]) is not None  # month must be a number
            and int(elements[2]) is not None  # day must be a number
            and 1 <= int(elements[1]) <= 12  # from january to december
            and 1 <= int(elements[2]) <= 31  # acceptable month days
        ):
            # Note: perhaps we could have better/more
            #       specific validation for the day of month
            yield FATAL, Message(
                "malformed",
                f"The date_added field has invalid format."
                f" It should be YYYY-MM-DD instead of '{family_metadata.date_added}'",
            )
