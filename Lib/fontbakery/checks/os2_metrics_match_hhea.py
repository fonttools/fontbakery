import os

from fontbakery.prelude import check, Message, PASS, FAIL


@check(
    id="os2_metrics_match_hhea",
    conditions=["not is_cjk_font"],
    rationale="""
        OS/2 and hhea vertical metric values should match. This will produce the
        same linespacing on Mac, GNU+Linux and Windows.

        - Mac OS X uses the hhea values.
        - Windows uses OS/2 or Win, depending on the OS or fsSelection bit value.

        When OS/2 and hhea vertical metrics match, the same linespacing results on
        macOS, GNU+Linux and Windows. Note that fixing this issue in a previously
        released font may cause reflow in user documents and unhappy users.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_os2_metrics_match_hhea(ttFont):
    """Checking OS/2 Metrics match hhea Metrics."""

    filename = os.path.basename(ttFont.reader.file.name)

    # Check both OS/2 and hhea are present.
    missing_tables = False

    required = ["OS/2", "hhea"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL, Message(f"lacks-{key}", f"{filename} lacks a '{key}' table.")

    if missing_tables:
        return

    # OS/2 sTypoAscender and sTypoDescender match hhea ascent and descent
    if ttFont["OS/2"].sTypoAscender != ttFont["hhea"].ascent:
        yield FAIL, Message(
            "ascender",
            f"OS/2 sTypoAscender ({ttFont['OS/2'].sTypoAscender})"
            f" and hhea ascent ({ttFont['hhea'].ascent}) must be equal.",
        )
    elif ttFont["OS/2"].sTypoDescender != ttFont["hhea"].descent:
        yield FAIL, Message(
            "descender",
            f"OS/2 sTypoDescender ({ttFont['OS/2'].sTypoDescender})"
            f" and hhea descent ({ttFont['hhea'].descent}) must be equal.",
        )
    elif ttFont["OS/2"].sTypoLineGap != ttFont["hhea"].lineGap:
        yield FAIL, Message(
            "lineGap",
            f"OS/2 sTypoLineGap ({ttFont['OS/2'].sTypoLineGap})"
            f" and hhea lineGap ({ttFont['hhea'].lineGap}) must be equal.",
        )
    else:
        yield PASS, "OS/2.sTypoAscender/Descender values match hhea.ascent/descent."
