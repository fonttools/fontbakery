import os

from fontbakery.prelude import check, Message, WARN
from fontbakery.testable import Font


def github_gfonts_description(font: Font, network, config):
    """Get the contents of the DESCRIPTION.en_us.html file
    from the google/fonts github repository corresponding
    to a given ttFont.
    """
    license_file = font.license_filename  # pytype: disable=attribute-error
    if not license_file or not network:
        return None

    import requests

    LICENSE_DIRECTORY = {"OFL.txt": "ofl", "UFL.txt": "ufl", "LICENSE.txt": "apache"}
    filename = os.path.basename(font.file)
    familyname = filename.split("-")[0].lower()
    url = (
        f"https://github.com/google/fonts/raw/main"
        f"/{LICENSE_DIRECTORY[license_file]}/{familyname}/DESCRIPTION.en_us.html"
    )
    try:
        return requests.get(url, timeout=config.get("timeout")).text
    except requests.RequestException:
        return None


@check(
    id="googlefonts/description/family_update",
    rationale="""
        We want to ensure that any significant changes to the font family are
        properly mentioned in the DESCRIPTION file.

        In general, it means that the contents of the DESCRIPTION.en_us.html file
        will typically change if when font files are updated. Please treat this check
        as a reminder to do so whenever appropriate!
    """,
    conditions=["description", "network"],
    proposal="https://github.com/fonttools/fontbakery/issues/3182",
)
def check_description_family_update(font, network, config):
    """
    On a family update, the DESCRIPTION.en_us.html file should ideally also be updated.
    """
    remote_description = github_gfonts_description(font, network, config)
    if remote_description == font.description:
        yield WARN, Message(
            "description-not-updated",
            "The DESCRIPTION.en_us.html file in this family has not changed"
            " in comparison to the latest font release on the"
            " google/fonts github repo.\n"
            "Please consider mentioning note-worthy improvements made"
            " to the family recently.",
        )
