from fontbakery.prelude import check, Message, WARN
from fontbakery.utils import (
    bullet_list,
    exit_with_install_instructions,
)
from fontbakery.checks.vendorspecific.typenetwork.glyphsets import TN_latin_set


@check(
    id="typenetwork/glyph_coverage",
    rationale="""
        Type Network expects that fonts in its catalog support at least the minimal
        set of characters.
    """,
    conditions=["font_codepoints"],
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_glyph_coverage(ttFont, font_codepoints, config):
    """Check Type Network minimum glyph coverage."""
    try:
        import unicodedata2
    except ImportError:
        exit_with_install_instructions("typenetwork")

    required_codepoints = set(TN_latin_set)
    diff = required_codepoints - font_codepoints
    missing = []
    for c in sorted(diff):
        try:
            missing.append("uni%04X %s (%s)\n" % (c, chr(c), unicodedata2.name(chr(c))))
        except ValueError:
            pass
    if missing:
        yield WARN, Message(
            "missing-codepoints",
            f"Missing required codepoints:\n\n{bullet_list(config, missing)}",
        )
