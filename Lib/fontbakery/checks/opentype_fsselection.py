from fontbakery.prelude import check, Message, FAIL


@check(
    id="opentype/fsselection",
    conditions=["style"],
    rationale="""
    The OS/2.fsSelection field is a bit field used to specify the stylistic
    qualities of the font - in particular, it specifies to some operating
    systems whether the font is italic (bit 0), bold (bit 5) or regular
    (bit 6).

    This check verifies that the fsSelection field is set correctly for the
    font style. For a family of static fonts created in GlyphsApp, this is
    set by using the style linking checkboxes in the exports settings.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_fsselection(ttFont, style):
    """Checking OS/2 fsSelection value."""
    from fontbakery.constants import RIBBI_STYLE_NAMES, STATIC_STYLE_NAMES, FsSelection
    from fontbakery.utils import check_bit_entry

    # Checking fsSelection REGULAR bit:
    expected = "Regular" in style or (
        style in STATIC_STYLE_NAMES
        and style not in RIBBI_STYLE_NAMES
        and "Italic" not in style
    )
    yield check_bit_entry(
        ttFont,
        "OS/2",
        "fsSelection",
        expected,
        bitmask=FsSelection.REGULAR,
        bitname="REGULAR",
    )

    # Checking fsSelection ITALIC bit:
    expected = "Italic" in style
    yield check_bit_entry(
        ttFont,
        "OS/2",
        "fsSelection",
        expected,
        bitmask=FsSelection.ITALIC,
        bitname="ITALIC",
    )

    # Checking fsSelection BOLD bit:
    expected = style in ["Bold", "BoldItalic"]
    yield check_bit_entry(
        ttFont,
        "OS/2",
        "fsSelection",
        expected,
        bitmask=FsSelection.BOLD,
        bitname="BOLD",
    )


@check(
    id="opentype/fsselection_matches_macstyle",
    rationale="""
        The bold and italic bits in OS/2.fsSelection must match the bold and italic
        bits in head.macStyle per the OpenType spec.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2382",
)
def check_fsselection_matches_macstyle(ttFont):
    """Check if OS/2 fsSelection matches head macStyle bold and italic bits."""

    # Check both OS/2 and head are present.
    missing_tables = False

    required = ["OS/2", "head"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL, Message(f"lacks-{key}", f"The '{key}' table is missing.")
    if missing_tables:
        return

    from fontbakery.constants import FsSelection, MacStyle

    head_bold = (ttFont["head"].macStyle & MacStyle.BOLD) != 0
    os2_bold = (ttFont["OS/2"].fsSelection & FsSelection.BOLD) != 0
    if head_bold != os2_bold:
        yield FAIL, Message(
            "fsselection-macstyle-bold",
            "The OS/2.fsSelection and head.macStyle bold settings do not match:\n\n"
            f"* OS/2.fsSelection: BOLD is {'not ' if not os2_bold else ''}set\n"
            f"* head.macStyle: BOLD is {'not ' if not head_bold else ''}set",
        )
    head_italic = (ttFont["head"].macStyle & MacStyle.ITALIC) != 0
    os2_italic = (ttFont["OS/2"].fsSelection & FsSelection.ITALIC) != 0
    if head_italic != os2_italic:
        yield FAIL, Message(
            "fsselection-macstyle-italic",
            "The OS/2.fsSelection and head.macStyle italic settings do not match.\n\n"
            f"* OS/2.fsSelection: ITALIC is {'not ' if not os2_italic else ''}set\n"
            f"* head.macStyle: ITALIC is {'not ' if not head_italic else ''}set",
        )
