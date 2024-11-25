from fontbakery.prelude import check, Message, WARN
from fontbakery.constants import NameID


@check(
    id="googlefonts/name/description_max_length",
    rationale="""
        An old FontLab version had a bug which caused it to store copyright notices
        in nameID 10 entries.

        In order to detect those and distinguish them from actual legitimate usage of
        this name table entry, we expect that such strings do not exceed a reasonable
        length of 200 chars.

        Longer strings are likely instances of the FontLab bug.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_description_max_length(ttFont):
    """Description strings in the name table must not exceed 200 characters."""
    for name in ttFont["name"].names:
        if (
            name.nameID == NameID.DESCRIPTION
            and len(name.string.decode(name.getEncoding())) > 200
        ):
            yield WARN, Message(
                "too-long",
                f"A few name table entries with ID={NameID.DESCRIPTION}"
                f" (NameID.DESCRIPTION) are longer than 200 characters."
                f" Please check whether those entries are copyright"
                f" notices mistakenly stored in the description"
                f" string entries by a bug in an old FontLab version."
                f" If that's the case, then such copyright notices"
                f" must be removed from these entries.",
            )
            return
