import re

from fontbakery.prelude import check, WARN, FAIL, Message
from fontbakery.constants import NameID


MANUFACTURERS_URLS = {
    "Adobe Systems Incorporated": "http://www.adobe.com/type/",
    "Ek Type": "http://www.ektype.in",
    "Monotype Imaging Inc.": "http://www.monotype.com/studio",
    "JamraPatel LLC": "http://www.jamra-patel.com",
    "Danh Hong": "http://www.khmertype.org",
    "Google LLC": "http://www.google.com/get/noto/",
    "Dalton Maag Ltd": "http://www.daltonmaag.com/",
    "Lisa Huang": "http://www.lisahuang.work",
    "Mangu Purty": "",
    "LiuZhao Studio": "",
}


@check(
    id="notofonts/name/manufacturer",
    rationale="""
        Noto fonts must contain known manufacturer and manufacturer
        URL entries in the name table.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_manufacturer(ttFont):
    """Ensure the manufacturer is a known Noto manufacturer and the URL is correct."""
    from fontbakery.utils import get_name_entry_strings

    manufacturers = get_name_entry_strings(ttFont, NameID.MANUFACTURER_NAME)
    good_manufacturer = None
    if not manufacturers:
        yield FAIL, Message(
            "no-manufacturer", "The font contained no manufacturer name."
        )

    manufacturer_re = "|".join(MANUFACTURERS_URLS.keys())
    for manufacturer in manufacturers:
        m = re.search(manufacturer_re, manufacturer)
        if m:
            good_manufacturer = m[0]
        else:
            yield WARN, Message(
                "unknown-manufacturer",
                f"The font's manufacturer name '{manufacturer}' was"
                f" not a known Noto font manufacturer.",
            )

    designer_urls = get_name_entry_strings(ttFont, NameID.DESIGNER_URL)
    if not designer_urls:
        yield WARN, Message("no-designer-urls", "The font contained no designer URL.")

    if good_manufacturer:
        expected_url = MANUFACTURERS_URLS[good_manufacturer]
        for designer_url in designer_urls:
            if designer_url != expected_url:
                yield WARN, Message(
                    "bad-designer-url",
                    f"The font's designer URL was '{designer_url}'"
                    f" but should have been '{expected_url}'.",
                )
