import os

from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/valid_filename_values",
    conditions=[
        "style",
        "family_metadata",
    ],
    rationale="""
        This check ensures that the font.filename field in the METADATA.pb
        is correct and well-formatted; we check well-formatting because we
        have a condition called 'style', and if that is true, then the font's
        filename correctly reflects its style. If a correctly formatted
        filename appears in the font.filename field in METADATA.pb, then all
        is good.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_metadata_valid_filename_values(font, family_metadata):
    """METADATA.pb font.filename field contains font name in right format?"""
    expected = os.path.basename(font.file)
    passed = False
    for font_metadata in family_metadata.fonts:
        if font_metadata.filename == expected:
            passed = True
            break

    if not passed:
        yield FAIL, Message(
            "bad-field",
            f"None of the METADATA.pb filename fields match"
            f' correct font name format ("{expected}").',
        )
