from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import NameID
from fontbakery.utils import markdown_table


@check(
    id="opentype/postscript_name",
    proposal="https://github.com/miguelsousa/openbakery/issues/62",
    rationale="""
        The PostScript name is used by some applications to identify the font.
        It should only consist of characters from the set A-Z, a-z, 0-9, and hyphen.

    """,
)
def check_postscript_name(ttFont):
    """PostScript name follows OpenType specification requirements?"""
    import re
    from fontbakery.utils import get_name_entry_strings

    bad_entries = []

    # <Postscript name> may contain only a-zA-Z0-9
    # and one hyphen
    bad_psname = re.compile("[^A-Za-z0-9-]")
    for string in get_name_entry_strings(ttFont, NameID.POSTSCRIPT_NAME):
        if bad_psname.search(string):
            bad_entries.append(
                {
                    "Field": "PostScript Name",
                    "Value": string,
                    "Recommendation": (
                        "May contain only a-zA-Z0-9 characters and a hyphen."
                    ),
                }
            )

    if len(bad_entries) > 0:
        yield FAIL, Message(
            "bad-psname-entries",
            f"PostScript name does not follow requirements:\n\n"
            f"{markdown_table(bad_entries)}",
        )
