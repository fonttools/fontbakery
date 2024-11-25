import requests

from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.checks.vendorspecific.googlefonts.utils import (
    get_DesignerInfoProto_Message,
)


@check(
    id="googlefonts/metadata/designer_profiles",
    rationale="""
        Google Fonts has a catalog of designers.

        This check ensures that the online entries of the catalog can be found based
        on the designer names listed on the METADATA.pb file.

        It also validates the URLs and file formats are all correctly set.
    """,
    conditions=["network", "family_metadata", "not is_noto"],
    proposal="https://github.com/fonttools/fontbakery/issues/3083",
)
def check_metadata_designer_profiles(family_metadata, config):
    """METADATA.pb: Designers are listed correctly on the Google Fonts catalog?"""
    DESIGNER_INFO_RAW_URL = (
        "https://raw.githubusercontent.com/google/fonts/master/catalog/designers/{}/"
    )

    # NOTE: See issue #3316
    TRANSLATE = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "à": "a",
        "è": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
        "ń": "n",
        "ø": "o",
        "ř": "r",
        "ś": "s",
        "ß": "ss",
        "ł": "l",
        "ã": "a",
        "ı": "i",
        "ü": "ue",
    }

    def normalize(name):
        """Restrict the designer name to lowercase a-z and numbers"""
        import string

        normalized_name = ""
        for c in name.lower():
            if c in string.ascii_letters or c in "0123456789":
                normalized_name += c
            elif c in TRANSLATE.keys():
                normalized_name += TRANSLATE[c]
        return normalized_name

    for designer in family_metadata.designer.split(","):
        designer = designer.strip()
        normalized_name = normalize(designer)
        if normalized_name == "multipledesigners":
            yield FAIL, Message(
                "multiple-designers",
                f"Font family {family_metadata.name} does not explicitely"
                f" mention the names of its designers on its METADATA.pb file.",
            )
            continue

        url = DESIGNER_INFO_RAW_URL.format(normalized_name) + "info.pb"
        response = requests.get(url, timeout=config.get("timeout"))

        # https://github.com/fonttools/fontbakery/pull/3892#issuecomment-1248758859
        # For debugging purposes:
        # yield WARN,\
        #      Message("config",
        #              f"Config is '{config}'")

        if response.status_code != requests.codes.OK:
            yield WARN, Message(
                "profile-not-found",
                f"It seems that {designer} is still not listed on"
                f" the designers catalog. Please submit a photo and"
                f" a link to a webpage where people can learn more"
                f" about the work of this designer/typefoundry.",
            )
            continue

        info = get_DesignerInfoProto_Message(response.content)
        if info.designer != designer.strip():
            yield FAIL, Message(
                "mismatch",
                f"Designer name at METADATA.pb ({designer})"
                f" is not the same as listed on the designers"
                f" catalog ({info.designer}) available at {url}",
            )

        if info.link != "":
            yield FAIL, Message(
                "link-field",
                "Currently the link field is not used by the GFonts API."
                " Designer webpage links should, for now, be placed"
                " directly on the bio.html file.",
            )

        if not info.avatar.file_name and designer != "Google":
            yield FAIL, Message(
                "missing-avatar",
                f"Designer {designer} still does not have an avatar image. "
                f"Please provide one.",
            )
        else:
            avatar_url = (
                DESIGNER_INFO_RAW_URL.format(normalized_name) + info.avatar.file_name
            )
            response = requests.get(avatar_url, timeout=config.get("timeout"))
            if response.status_code != requests.codes.OK:
                yield FAIL, Message(
                    "bad-avatar-filename",
                    "The avatar filename provided seems to be incorrect:"
                    f" ({avatar_url})",
                )
