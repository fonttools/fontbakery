from fontbakery.prelude import PASS, FAIL, Message, check


@check(
    id="legacy_accents",
    rationale="""
        Legacy accents should not have anchors and should have positive width.
        They are often used independently of a letter, either as a placeholder
        for an expected combined mark+letter combination in MacOS, or separately.
        For instance, U+00B4 (ACUTE ACCENT) is often mistakenly used as an apostrophe,
        U+0060 (GRAVE ACCENT) is used in Markdown to notify code blocks,
        and ^ is used as an exponential operator in maths.
    """,
    proposal=[
        "https://github.com/googlefonts/fontbakery/issues/4310",
    ],
)
def check_legacy_accents(ttFont):
    """Check that legacy accents aren't used in composite glyphs."""

    # code-points for all legacy chars
    LEGACY_ACCENTS = {
        0x00A8,  # DIAERESIS
        0x02D9,  # DOT ABOVE
        0x0060,  # GRAVE ACCENT
        0x00B4,  # ACUTE ACCENT
        0x02DD,  # DOUBLE ACUTE ACCENT
        0x02C6,  # MODIFIER LETTER CIRCUMFLEX ACCENT
        0x02C7,  # CARON
        0x02D8,  # BREVE
        0x02DA,  # RING ABOVE
        0x02DC,  # SMALL TILDE
        0x00AF,  # MACRON
        0x00B8,  # CEDILLA
        0x02DB,  # OGONEK
    }

    passed = True

    reverseCmap = ttFont["cmap"].buildReversed()
    hmtx = ttFont["hmtx"]

    # Check whether legacy accents have positive width.
    for name in reverseCmap:
        if reverseCmap[name].intersection(LEGACY_ACCENTS):
            if hmtx[name][0] == 0:
                passed = False
                yield FAIL, Message(
                    "legacy-accents-width",
                    f'Width of legacy accent "{name}" is zero; should be positive.',
                )

    # Check whether legacy accents appear in GDEF as marks.
    # Not being marks in GDEF also typically means that they don't have anchors,
    # as font compilers would have otherwise classified them as marks in GDEF.
    if "GDEF" in ttFont and ttFont["GDEF"].table.GlyphClassDef:
        class_def = ttFont["GDEF"].table.GlyphClassDef.classDefs
        for name in reverseCmap:
            if reverseCmap[name].intersection(LEGACY_ACCENTS):
                if name in class_def and class_def[name] == 3:
                    passed = False
                    yield FAIL, Message(
                        "legacy-accents-gdef",
                        f'Legacy accent "{name}" is defined in GDEF'
                        f" as a mark (class 3).",
                    )

    if passed:
        yield PASS, "Looks good!"
