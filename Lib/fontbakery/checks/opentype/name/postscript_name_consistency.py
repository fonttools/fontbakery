from fontbakery.prelude import check, Message, FAIL
from fontbakery.constants import NameID


@check(
    id="opentype/name/postscript_name_consistency",
    conditions=["not is_cff"],  # e.g. TTF or CFF2
    rationale="""
        The PostScript name entries in the font's 'name' table should be
        consistent across platforms.

        This is the TTF/CFF2 equivalent of the CFF 'name/postscript_vs_cff' check.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2394",
)
def check_name_postscript_name_consistency(ttFont):
    """Name table ID 6 (PostScript name) must be consistent across platforms."""
    postscript_names = set()
    for entry in ttFont["name"].names:
        if entry.nameID == NameID.POSTSCRIPT_NAME:
            postscript_name = entry.toUnicode()
            postscript_names.add(postscript_name)

    if len(postscript_names) > 1:
        yield FAIL, Message(
            "inconsistency",
            f'Entries in the "name" table for ID 6'
            f" (PostScript name) are not consistent."
            f" Names found: {sorted(postscript_names)}.",
        )
