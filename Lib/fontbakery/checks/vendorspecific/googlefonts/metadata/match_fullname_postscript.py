from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/match_fullname_postscript",
    conditions=["font_metadata"],
    rationale="""
        The font.full_name and font.post_script_name fields in the
        METADATA.pb file should be consistent - i.e. when all non-alphabetic
        characters are removed, they should be the same. This is to
        prevent inconsistencies when one or the other value has been
        manually edited in the METADATA.pb file.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_match_fullname_postscript(font_metadata):
    """METADATA.pb font.full_name and font.post_script_name
    fields have equivalent values ?
    """
    import re

    regex = re.compile(r"\W")
    post_script_name = regex.sub("", font_metadata.post_script_name)
    fullname = regex.sub("", font_metadata.full_name)
    if fullname != post_script_name:
        yield FAIL, Message(
            "mismatch",
            f'METADATA.pb font full_name = "{font_metadata.full_name}" does not match'
            f' post_script_name = "{font_metadata.post_script_name}"',
        )
