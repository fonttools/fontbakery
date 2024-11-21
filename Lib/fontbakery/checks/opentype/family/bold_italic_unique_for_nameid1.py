from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/family/bold_italic_unique_for_nameid1",
    conditions=["RIBBI_ttFonts"],
    rationale="""
        Per the OpenType spec: name ID 1 'is used in combination with Font Subfamily
        name (name ID 2), and should be shared among at most four fonts that differ
        only in weight or style.

        This four-way distinction should also be reflected in the OS/2.fsSelection
        field, using bits 0 and 5.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2388",
)
def check_family_bold_italic_unique_for_nameid1(RIBBI_ttFonts):
    """Check that OS/2.fsSelection bold & italic settings are unique
    for each NameID1"""
    from collections import Counter

    from fontbakery.constants import FsSelection, NameID
    from fontbakery.utils import get_name_entry_strings

    family_name_and_bold_italic = []
    for ttFont in RIBBI_ttFonts:
        names_list = get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)
        # names_list will likely contain multiple entries, e.g. multiple copies
        # of the same name in the same language for different platforms, but
        # also different names in different languages, we use set() below
        # to remove the duplicates and only store the unique family name(s)
        # used for a given font
        names_set = set(names_list)

        bold = (ttFont["OS/2"].fsSelection & FsSelection.BOLD) != 0
        italic = (ttFont["OS/2"].fsSelection & FsSelection.ITALIC) != 0
        bold_italic = "Bold=%r, Italic=%r" % (bold, italic)

        for name in names_set:
            family_name_and_bold_italic.append(
                (
                    name,
                    bold_italic,
                )
            )

    counter = Counter(family_name_and_bold_italic)
    for (family_name, bold_italic), count in counter.items():
        if count > 1:
            yield FAIL, Message(
                "unique-fsselection",
                f"Family '{family_name}' has {count} fonts"
                f" (should be no more than 1) with the"
                f" same OS/2.fsSelection bold & italic settings:"
                f" {bold_italic}",
            )
