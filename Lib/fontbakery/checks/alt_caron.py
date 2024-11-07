from fontbakery.prelude import PASS, FAIL, WARN, Message, check


@check(
    id="alt_caron",
    conditions=["is_ttf"],
    rationale="""
        Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright
        or quotesingle or comma or caron(comb). It should be composed with a
        distinctive glyph which doesn't look like an apostrophe.

        Source:
        https://ilovetypography.com/2009/01/24/on-diacritics/
        http://diacritics.typo.cz/index.php?id=5
        https://www.typotheque.com/articles/lcaron
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3308",
)
def check_alt_caron(ttFont):
    """Check accent of Lcaron, dcaron, lcaron, tcaron"""

    CARON_GLYPHS = set(
        (
            0x013D,  # LATIN CAPITAL LETTER L WITH CARON
            0x010F,  # LATIN SMALL LETTER D WITH CARON
            0x013E,  # LATIN SMALL LETTER L WITH CARON
            0x0165,  # LATIN SMALL LETTER T WITH CARON
        )
    )

    WRONG_CARON_MARKS = set(
        (
            0x02C7,  # CARON
            0x030C,  # COMBINING CARON
        )
    )

    # This may be expanded to include other comma-lookalikes:
    BAD_CARON_MARKS = set(
        (
            0x002C,  # COMMA
            0x2019,  # RIGHT SINGLE QUOTATION MARK
            0x201A,  # SINGLE LOW-9 QUOTATION MARK
            0x0027,  # APOSTROPHE
        )
    )

    passed = True

    glyphOrder = ttFont.getGlyphOrder()
    reverseCmap = ttFont["cmap"].buildReversed()

    for name in glyphOrder:
        if reverseCmap.get(name, set()).intersection(CARON_GLYPHS):
            glyph = ttFont["glyf"][name]
            if not glyph.isComposite():
                yield WARN, Message(
                    "decomposed-outline",
                    f"{name} is decomposed and therefore could not be checked."
                    f" Please check manually.",
                )
                continue
            if len(glyph.components) == 1:
                yield WARN, Message(
                    "single-component",
                    f"{name} is composed of a single component and therefore"
                    f" could not be checked. Please check manually.",
                )
            if len(glyph.components) > 1:
                for component in glyph.components:
                    # Uses absolutely wrong caron mark
                    # Purge other endings in the future (not .alt)
                    codepoints = reverseCmap.get(
                        component.glyphName.replace(".case", "")
                        .replace(".uc", "")
                        .replace(".sc", ""),
                        set(),
                    )
                    if codepoints.intersection(WRONG_CARON_MARKS):
                        passed = False
                        yield FAIL, Message(
                            "wrong-mark",
                            f"{name} uses component {component.glyphName}.",
                        )

                    # Uses bad mark
                    if codepoints.intersection(BAD_CARON_MARKS):
                        yield WARN, Message(
                            "bad-mark", f"{name} uses component {component.glyphName}."
                        )
    if passed:
        yield PASS, "Looks good!"
