from fontbakery.prelude import check, Message, INFO
from fontbakery.constants import NameID


@check(
    id="opentype/family_naming_recommendations",
    rationale="""
        This check ensures that the length of various family name and style
        name strings in the name table are within the maximum length
        recommended by the OpenType specification.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_family_naming_recommendations(ttFont):
    """Font follows the family naming recommendations?"""
    # See http://forum.fontlab.com/index.php?topic=313.0

    from fontbakery.utils import get_name_entry_strings

    bad_entries = []

    for string in get_name_entry_strings(ttFont, NameID.FULL_FONT_NAME):
        if len(string) >= 64:
            bad_entries.append(
                {
                    "field": "Full Font Name",
                    "value": string,
                    "rec": "exceeds max length (63)",
                }
            )

    for string in get_name_entry_strings(ttFont, NameID.POSTSCRIPT_NAME):
        if len(string) >= 64:
            bad_entries.append(
                {
                    "field": "PostScript Name",
                    "value": string,
                    "rec": "exceeds max length (63)",
                }
            )

    for string in get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME):
        if len(string) >= 32:
            bad_entries.append(
                {
                    "field": "Family Name",
                    "value": string,
                    "rec": "exceeds max length (31)",
                }
            )

    for string in get_name_entry_strings(ttFont, NameID.FONT_SUBFAMILY_NAME):
        if len(string) >= 32:
            bad_entries.append(
                {
                    "field": "Style Name",
                    "value": string,
                    "rec": "exceeds max length (31)",
                }
            )

    for string in get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME):
        if len(string) >= 32:
            bad_entries.append(
                {
                    "field": "OT Family Name",
                    "value": string,
                    "rec": "exceeds max length (31)",
                }
            )

    for string in get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_SUBFAMILY_NAME):
        if len(string) >= 32:
            bad_entries.append(
                {
                    "field": "OT Style Name",
                    "value": string,
                    "rec": "exceeds max length (31)",
                }
            )

    if len(bad_entries) > 0:
        table = "| Field | Value | Recommendation |\n"
        table += "|:----- |:----- |:-------------- |\n"
        for bad in bad_entries:
            table += "| {} | {} | {} |\n".format(bad["field"], bad["value"], bad["rec"])
        yield INFO, Message(
            "bad-entries",
            f"Font does not follow "
            f"some family naming recommendations:\n"
            f"\n"
            f"{table}",
        )
