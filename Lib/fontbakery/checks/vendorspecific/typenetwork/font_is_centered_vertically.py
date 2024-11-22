from fontbakery.prelude import check, Message, PASS, FAIL, WARN


@check(
    id="typenetwork/font_is_centered_vertically",
    rationale="""
        FIXME! This check still does not have rationale documentation.
    """,
    proposal=["https://github.com/fonttools/fontbakery/pull/4260"],
)
def check_font_is_centered_vertically(ttFont):
    """Checking if font is vertically centered."""

    # Check required tables exist on font
    required_tables = {"hhea", "OS/2"}
    missing_tables = sorted(required_tables - set(ttFont.keys()))
    if missing_tables:
        for table_tag in missing_tables:
            yield FAIL, Message("lacks-table", f"Font lacks '{table_tag}' table.")
        return

    capHeight = ttFont["OS/2"].sCapHeight
    ascent = ttFont["hhea"].ascent - capHeight
    descent = abs(ttFont["hhea"].descent)

    ratio = abs(ascent - descent) / max(ascent, descent)
    threshold1 = 0.1
    threshold2 = 0.3

    if threshold1 >= ratio > threshold2:
        yield WARN, Message(
            "uncentered",
            "The font will display slightly vertically uncentered on"
            " web environments.",
        )
        yield WARN, Message(
            "uncentered",
            f"The font will display vertically uncentered on"
            f" web environments. Top space above cap height is {ascent}"
            f" and under baseline is {descent}",
        )
    elif ratio >= threshold2:
        yield FAIL, Message(
            "very-uncentered",
            f"The font will display significantly vertically uncentered on"
            f" web environments. Top space above cap height is {ascent}"
            f" and under baseline is {descent}",
        )
    else:
        yield PASS, Message(
            "centered",
            "The font will display vertically centered on web environments.",
        )
