from fontbakery.constants import NameID
from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/nameid/post_script_name",
    conditions=["font_metadata"],
    rationale="""
        This check ensures that the PostScript name declared in the METADATA.pb file
        matches the PostScript name declared in the name table of the font file.
        If the font was uploaded by the packager, this should always be the
        case. But if there were manual changes to the METADATA.pb file, a mismatch
        could occur.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_nameid_post_script_name(ttFont, font_metadata):
    """Checks METADATA.pb font.post_script_name matches
    postscript name declared on the name table.
    """
    from fontbakery.utils import get_name_entry_strings

    postscript_names = get_name_entry_strings(ttFont, NameID.POSTSCRIPT_NAME)
    if len(postscript_names) == 0:
        yield FAIL, Message(
            "missing",
            (
                f"This font lacks a POSTSCRIPT_NAME entry"
                f" (nameID = {NameID.POSTSCRIPT_NAME}) in the name table."
            ),
        )
    else:
        for psname in postscript_names:
            if psname != font_metadata.post_script_name:
                yield FAIL, Message(
                    "mismatch",
                    (
                        f"Unmatched postscript name in font:"
                        f' TTF has "{psname}" while METADATA.pb has'
                        f' "{font_metadata.post_script_name}".'
                    ),
                )
