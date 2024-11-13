from fontbakery.prelude import PASS, WARN, Message, check
from fontbakery.utils import feature_tags


@check(
    id="cjk_chws_feature",
    conditions=["is_cjk_font"],
    rationale="""
        The W3C recommends the addition of chws and vchw features to CJK fonts
        to enhance the spacing of glyphs in environments which do not fully support
        JLREQ layout rules.

        The chws_tool utility (https://github.com/googlefonts/chws_tool) can be used
        to add these features automatically.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3363",
)
def check_cjk_chws_feature(ttFont):
    """Does the font contain chws and vchw features?"""
    passed = True
    tags = feature_tags(ttFont)
    FEATURE_NOT_FOUND = (
        "{} feature not found in font."
        " Use chws_tool (https://github.com/googlefonts/chws_tool)"
        " to add it."
    )
    if "chws" not in tags:
        passed = False
        yield WARN, Message("missing-chws-feature", FEATURE_NOT_FOUND.format("chws"))
    if "vchw" not in tags:
        passed = False
        yield WARN, Message("missing-vchw-feature", FEATURE_NOT_FOUND.format("vchw"))
    if passed:
        yield PASS, "Font contains chws and vchw features"
