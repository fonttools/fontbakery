import os

from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/match_filename_postscript",
    conditions=["font_metadata", "not is_variable_font"],
    # FIXME: We'll want to review this once
    #        naming rules for varfonts are settled.
    rationale="""
        For static fonts, this checks that the font filename as declared in
        the METADATA.pb file matches the post_script_name field. i.e.
        SomeFont-Regular.ttf should have a PostScript name of SomeFont-Regular.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_match_filename_postscript(font_metadata):
    """METADATA.pb font.filename and font.post_script_name
    fields have equivalent values?
    """
    post_script_name = font_metadata.post_script_name
    filename = os.path.splitext(font_metadata.filename)[0]

    if filename != post_script_name:
        yield FAIL, Message(
            "mismatch",
            f'METADATA.pb font filename = "{font_metadata.filename}" does not match'
            f' post_script_name="{font_metadata.post_script_name}".',
        )
