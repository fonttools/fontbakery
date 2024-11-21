from fontbakery.prelude import check, FAIL, Message
from fontbakery.checks.iso15008.utils import (
    stem_width,
    DISCLAIMER,
)


@check(
    id="iso15008/stem_width",
    rationale="""
        According to ISO 15008, fonts used for in-car displays should
        not be too light or too bold.

        To ensure legibility of this font on in-car information systems,
        it is recommended that the ratio of stem width to ascender height
        is between 0.10 and 0.20.
    """
    + DISCLAIMER,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/1832",
        "https://github.com/fonttools/fontbakery/issues/3251",
    ],
)
def check_iso15008_stem_width(ttFont):
    """Check if 0.10 <= (stem width / ascender) <= 0.82"""
    width = stem_width(ttFont)
    if width is None:
        yield FAIL, Message("no-stem-width", "Could not determine stem width")
        return
    ascender = ttFont["hhea"].ascender
    proportion = width / ascender
    if not 0.10 <= proportion <= 0.20:
        yield FAIL, Message(
            "invalid-proportion",
            f"The proportion of stem width to ascender ({proportion})"
            f"does not conform to the expected range of 0.10-0.20",
        )
