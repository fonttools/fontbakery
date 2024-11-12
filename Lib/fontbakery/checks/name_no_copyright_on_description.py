from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, FAIL


@check(
    id="name/no_copyright_on_description",
    rationale="""
        The name table in a font file contains strings about the font;
        there are entries for a copyright field and a description. If the
        copyright entry is being used correctly, then there should not
        be any copyright information in the description entry.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_name_no_copyright_on_description(ttFont):
    """Description strings in the name table must not contain copyright info."""
    for name in ttFont["name"].names:
        if (
            "opyright" in name.string.decode(name.getEncoding())
            and name.nameID == NameID.DESCRIPTION
        ):
            yield FAIL, Message(
                "copyright-on-description",
                f"Some namerecords with"
                f" ID={NameID.DESCRIPTION} (NameID.DESCRIPTION)"
                f" containing copyright info should be removed"
                f" (perhaps these were added by a longstanding"
                f" FontLab Studio 5.x bug that copied"
                f" copyright notices to them.)",
            )
            break
