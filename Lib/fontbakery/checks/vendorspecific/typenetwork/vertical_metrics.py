from fontbakery.prelude import check, Message, PASS, FAIL, WARN


@check(
    id="typenetwork/vertical_metrics",
    rationale="""
        OS/2 and hhea vertical metric values should match. This will produce the
        same linespacing on Mac, GNU+Linux and Windows.

        - Mac OS X uses the hhea values.⏎
        - Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.

        When OS/2 and hhea vertical metrics match, the same linespacing results on
        macOS, GNU+Linux and Windows.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_vertical_metrics(ttFont):
    """Checking vertical metrics."""

    # Check required tables exist on font
    required_tables = {"hhea", "OS/2"}
    missing_tables = sorted(required_tables - set(ttFont.keys()))
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

    useTypoMetric = ttFont["OS/2"].fsSelection & (1 << 7)

    hheaAscent_equals_typoAscent = ttFont["hhea"].ascent == ttFont["OS/2"].sTypoAscender
    hheaDescent_equals_typoDescent = abs(ttFont["hhea"].descent) == abs(
        ttFont["OS/2"].sTypoDescender
    )

    hheaAscent_equals_winAscent = ttFont["hhea"].ascent == ttFont["OS/2"].usWinAscent
    hheaDescent_equals_winDescent = (
        abs(ttFont["hhea"].descent) == ttFont["OS/2"].usWinDescent
    )

    typoMetricsSum = (
        ttFont["OS/2"].sTypoAscender
        + abs(ttFont["OS/2"].sTypoDescender)
        + ttFont["OS/2"].sTypoLineGap
    )
    hheaMetricsSum = (
        ttFont["hhea"].ascent + abs(ttFont["hhea"].descent) + ttFont["hhea"].lineGap
    )

    if useTypoMetric:
        if not hheaAscent_equals_typoAscent:
            yield FAIL, Message(
                "ascender",
                f"OS/2 sTypoAscender ({ttFont['OS/2'].sTypoAscender})"
                f" and hhea ascent ({ttFont['hhea'].ascent}) must be equal.",
            )
        elif not hheaDescent_equals_typoDescent:
            yield FAIL, Message(
                "descender",
                f"OS/2 sTypoDescender ({ttFont['OS/2'].sTypoDescender})"
                f" and hhea descent ({ttFont['hhea'].descent}) must be equal.",
            )
        elif ttFont["OS/2"].sTypoLineGap != 0:
            yield FAIL, Message("hhea", "typo lineGap is not equal to 0.")
        elif ttFont["hhea"].lineGap != 0:
            yield FAIL, Message("hhea", "hhea lineGap is not equal to 0.")
        else:
            yield PASS, "Typo and hhea metrics are equal."
    else:
        yield WARN, Message(
            "metrics-recommendation",
            "OS/2 fsSelection USE_TYPO_METRICS is not enabled.\n\n"
            "Type Networks recommends to enable it and follow the vertical metrics"
            " scheme where basically hhea matches typo metrics. Read in more detail"
            " about it in our vertical metrics guide.",
        )

        if hheaAscent_equals_typoAscent and hheaDescent_equals_winDescent:
            yield FAIL, Message(
                "useTypoMetricsDisabled",
                "OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is not enabled",
            )
        elif not hheaAscent_equals_winAscent:
            yield FAIL, Message(
                "ascender",
                f"hhea ascent ({ttFont['hhea'].ascent})"
                f" and OS/2 win ascent ({ttFont['OS/2'].usWinAscent}) must be equal.",
            )
        elif not hheaDescent_equals_winDescent:
            yield FAIL, Message(
                "descender",
                f"hhea descent ({ttFont['hhea'].descent})"
                f" and OS/2 win ascent ({ttFont['OS/2'].usWinDescent}) must be equal.",
            )
        elif typoMetricsSum != hheaMetricsSum:
            yield FAIL, Message(
                "typo-and-hhea-sum",
                f"OS/2 typo metrics sum ({typoMetricsSum}) must be"
                f" equal to win metrics sum ({hheaMetricsSum})",
            )
        else:
            yield PASS, "hhea and Win metrics are equal and useTypoMetrics is disabled."
