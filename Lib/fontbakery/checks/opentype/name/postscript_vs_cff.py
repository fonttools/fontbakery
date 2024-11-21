from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import NameID


@check(
    id="opentype/name/postscript_vs_cff",
    conditions=["is_cff"],
    rationale="""
        The PostScript name entries in the font's 'name' table should match
        the FontName string in the 'CFF ' table.

        The 'CFF ' table has a lot of information that is duplicated in other tables.
        This information should be consistent across tables, because there's
        no guarantee which table an app will get the data from.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2229",
)
def check_name_postscript_vs_cff(ttFont):
    """CFF table FontName must match name table ID 6 (PostScript name)."""
    cff_names = ttFont["CFF "].cff.fontNames
    if len(cff_names) != 1:
        yield FAIL, Message(
            "cff-name-error", "Unexpected number of font names in CFF table."
        )
        return

    cff_name = cff_names[0]
    for entry in ttFont["name"].names:
        if entry.nameID == NameID.POSTSCRIPT_NAME:
            postscript_name = entry.toUnicode()
            if postscript_name != cff_name:
                yield FAIL, Message(
                    "ps-cff-name-mismatch",
                    f"Name table PostScript name '{postscript_name}' "
                    f"does not match CFF table FontName '{cff_name}'.",
                )
