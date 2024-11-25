from fontbakery.prelude import check, Message, FAIL, WARN


# Although this is a /name/ check, it's really about licensing
@check(
    id="googlefonts/name/rfn",
    rationale="""
        Some designers adopt the "Reserved Font Name" clause of the OFL license. This
        means that the original author reserves the rights to the family name and other
        people can only distribute modified versions using a different family name.

        Google Fonts published updates to the fonts in the collection in order to fix
        issues and/or implement further improvements to the fonts. It is important to
        keep the family name so that users of the webfonts can benefit from the updates.
        Since it would forbid such usage scenario, all families in the GFonts collection
        are required to not adopt the RFN clause.

        This check ensures "Reserved Font Name" is not mentioned in the name table.
    """,
    conditions=["not rfn_exception"],
    proposal="https://github.com/fonttools/fontbakery/issues/1380",
)
def check_name_rfn(ttFont, familyname):
    """Name table strings must not contain the string 'Reserved Font Name'."""
    for entry in ttFont["name"].names:
        string = entry.toUnicode()
        if "This license is copied below, and is also available with a FAQ" in string:
            # This is the OFL text in a name table entry.
            # It contains the term 'Reserved Font Name' in one of its clauses,
            # so we will ignore this here.
            continue

        import re

        matches = re.search(r"with [Rr]eserved [Ff]ont [Nn]ame (.*)\.", string)

        if matches:
            reserved_font_name = matches.group(1)
            if reserved_font_name in familyname:
                yield FAIL, Message(
                    "rfn",
                    f'Name table entry contains "Reserved Font Name":\n'
                    f'\t"{string}"\n'
                    f"\n"
                    f"This is an error except in a few specific rare cases.",
                )
            else:
                yield WARN, Message(
                    "legacy-familyname",
                    f'Name table entry contains "Reserved Font Name" for a'
                    f" family name ({reserved_font_name}) that differs"
                    f" from the currently used family name ({familyname}),"
                    f" which is fine.",
                )
