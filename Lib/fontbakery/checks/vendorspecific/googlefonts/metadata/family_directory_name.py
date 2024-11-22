import os

from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/metadata/family_directory_name",
    rationale="""
        We want the directory name of a font family to be predictable and directly
        derived from the family name, all lowercased and removing spaces.
    """,
    conditions=["family_metadata", "family_directory"],
    proposal="https://github.com/fonttools/fontbakery/issues/3421",
)
def check_metadata_family_directory_name(family_metadata, family_directory):
    """Check font family directory name."""

    dir_name = os.path.basename(family_directory)
    expected = family_metadata.name.replace(" ", "").lower()
    if expected != dir_name:
        yield FAIL, Message(
            "bad-directory-name",
            f'Family name on METADATA.pb is "{family_metadata.name}"\n'
            f'Directory name is "{dir_name}"\n'
            f'Expected "{expected}"',
        )
