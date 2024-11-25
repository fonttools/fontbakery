import os

from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="googlefonts/repo/dirname_matches_nameid_1",
    conditions=["gfonts_repo_structure"],
    proposal="https://github.com/fonttools/fontbakery/issues/2302",
    rationale="""
        For static fonts, we expect to name the directory in google/fonts
        according to the NameID 1 of the regular font, all lower case with
        no hyphens or spaces. This check verifies that the directory
        name matches our expectations.
    """,
)
def check_repo_dirname_match_nameid_1(fonts):
    """Directory name in GFonts repo structure must
    match NameID 1 of the regular."""
    from fontTools.ttLib import TTFont
    from fontbakery.utils import get_name_entry_strings, get_regular

    if any(f.is_variable_font for f in fonts):
        yield SKIP, Message(
            "variable-exempt", "Variable fonts are exempt from this check."
        )
        return

    regular = get_regular(fonts)
    if not regular:
        yield FAIL, Message(
            "lacks-regular",
            "The font seems to lack a regular."
            " If family consists of a single-weight non-Regular style only,"
            " consider the Google Fonts specs for this case:"
            " https://github.com/googlefonts/gf-docs/tree/main/Spec#single-weight-families",  # noqa:E501 pylint:disable=C0301
        )
        return

    entry = get_name_entry_strings(TTFont(regular.file), NameID.FONT_FAMILY_NAME)[0]
    expected = entry.lower()
    expected = "".join(expected.split(" "))
    expected = "".join(expected.split("-"))

    _, familypath, _ = os.path.abspath(regular.file).split(os.path.sep)[-3:]
    if familypath != expected:
        yield FAIL, Message(
            "mismatch",
            f"Family name on the name table ('{entry}') does not match"
            f" directory name in the repo structure ('{familypath}')."
            f" Expected '{expected}'.",
        )
