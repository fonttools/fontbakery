import os

from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/filenames",
    rationale="""
        Note:
        This check only looks for files in the current directory.

        Font files in subdirectories are checked by these other two checks:
         - googlefonts/metadata/undeclared_fonts
         - googlefonts/repo/vf_has_static_fonts

        We may want to merge them all into a single check.
    """,
    conditions=["family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/2597",
)
def check_metadata_filenames(fonts, family_directory, family_metadata):
    """METADATA.pb: Font filenames match font.filename entries?"""

    metadata_filenames = []
    font_filenames = [
        f for f in os.listdir(family_directory) if f[-4:] in [".ttf", ".otf"]
    ]
    for font_metadata in family_metadata.fonts:
        if font_metadata.filename not in font_filenames:
            yield FAIL, Message(
                "file-not-found",
                f'Filename "{font_metadata.filename}" is listed on METADATA.pb'
                f" but an actual font file with that name was not found.",
            )
        metadata_filenames.append(font_metadata.filename)

    for font in font_filenames:
        if font not in metadata_filenames:
            yield FAIL, Message(
                "file-not-declared",
                f'Filename "{font}" is not declared'
                f" on METADATA.pb as a font.filename entry.",
            )
