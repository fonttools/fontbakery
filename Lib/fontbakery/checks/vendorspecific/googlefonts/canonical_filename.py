import os

from fontbakery.prelude import check, Message, PASS, FAIL
from fontbakery.utils import exit_with_install_instructions


@check(
    id="googlefonts/canonical_filename",
    rationale="""
        A font's filename must be composed as "<familyname>-<stylename>.ttf":

        - Nunito-Regular.ttf

        - Oswald-BoldItalic.ttf


        Variable fonts must list the axis tags in alphabetical order in
        square brackets and separated by commas:

        - Roboto[wdth,wght].ttf

        - Familyname-Italic[wght].ttf
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_canonical_filename(ttFont):
    """Checking file is named canonically."""

    try:
        import axisregistry
    except ImportError:
        exit_with_install_instructions("googlefonts")

    current_filename = os.path.basename(ttFont.reader.file.name)
    expected_filename = axisregistry.build_filename(ttFont)

    if current_filename != expected_filename:
        yield FAIL, Message(
            "bad-filename", f'Expected "{expected_filename}. Got {current_filename}.'
        )
    else:
        yield PASS, f'Font filename is correct, "{current_filename}".'
