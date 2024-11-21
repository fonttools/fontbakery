import re

from fontbakery.prelude import check, PASS, FAIL


@check(
    id="microsoft/vendor_url",
    rationale="""
        Check whether vendor URL is pointing at microsoft.com
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_vendor_url(ttFont):
    """Validate vendor URL."""
    name_record = ttFont["name"].getName(11, 3, 1, 0x0409)
    if name_record is None:
        yield FAIL, "Name ID 11 (vendor URL) does not exists."
    else:
        vendor_url = name_record.toUnicode()
        vendor_pattern = r"https?://(\w+\.)?microsoft.com/?"
        m = re.match(vendor_pattern, vendor_url)
        if m is None:
            yield FAIL, (f"vendor URL does not point at microsoft.com: '{vendor_url}'")
        else:
            yield PASS, "vendor URL OK"
