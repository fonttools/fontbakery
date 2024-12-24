from fontbakery.prelude import check, Message, FAIL, SKIP


@check(
    id="googlefonts/use_typo_metrics",
    rationale="""
        All fonts on the Google Fonts collection should have OS/2.fsSelection bit 7
        (USE_TYPO_METRICS) set. This requirement is part of the vertical metrics scheme
        established as a Google Fonts policy aiming at a common ground supported by
        all major font rendering environments.

        For more details, read:
        https://github.com/googlefonts/gf-docs/blob/main/VerticalMetrics/README.md

        Below is the portion of that document that is most relevant to this check:

        Use_Typo_Metrics must be enabled. This will force MS Applications to use the
        OS/2 Typo values instead of the Win values. By doing this, we can freely set
        the Win values to avoid clipping and control the line height with the typo
        values. It has the added benefit of future line height compatibility. When
        a new script is added, we simply change the Win values to the new yMin
        and yMax, without needing to worry if the line height have changed.
    """,
    severity=10,
    proposal="https://github.com/fonttools/fontbakery/issues/3241",
)
def check_use_typo_metrics(fonts):
    """OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is set in all fonts."""
    if any(font.is_cjk_font for font in fonts):
        yield SKIP, Message("cjk", "This check does not apply to CJK fonts.")
        return

    bad_fonts = []
    for font in fonts:
        if not font.ttFont["OS/2"].fsSelection & (1 << 7):
            bad_fonts.append(font.file)

    if bad_fonts:
        yield FAIL, Message(
            "missing-os2-fsselection-bit7",
            f"OS/2.fsSelection bit 7 (USE_TYPO_METRICS) was"
            f"NOT set in the following fonts: {bad_fonts}.",
        )
