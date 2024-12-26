from fontbakery.constants import FsSelection, MacStyle
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

        Additionally, the bold and italic bits in OS/2.fsSelection must match the
        bold and italic bits in head.macStyle per the OpenType spec.
    """,
    proposal=[
        "https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
        "https://github.com/fonttools/fontbakery/pull/2382",
    ],
)
def check_fsselection(ttFont, style):
    """Checking OS/2 fsSelection value."""

    # Check both OS/2 and head are present.
    missing_tables = False

    required = ["OS/2", "head"]
    for key in required:
        if key not in ttFont:
            missing_tables = True
            yield FAIL, Message(f"lacks-{key}", f"The '{key}' table is missing.")
    if missing_tables:
        return

    bold_expected = style in ["Bold", "BoldItalic"]
    italic_expected = "Italic" in style
    regular_expected = (not bold_expected) and (not italic_expected)
    bold_seen = bool(ttFont["OS/2"].fsSelection & FsSelection.BOLD)
    italic_seen = bool(ttFont["OS/2"].fsSelection & FsSelection.ITALIC)
    regular_seen = bool(ttFont["OS/2"].fsSelection & FsSelection.REGULAR)

    for flag, expected, label in [
        (bold_seen, bold_expected, "Bold"),
        (italic_seen, italic_expected, "Italic"),
        (regular_seen, regular_expected, "Regular"),
    ]:
        if flag != expected:
            yield FAIL, Message(
                f"bad-{label.upper()}",
                f"fsSelection {label} flag {flag}"
                f" does not match font style {style}",
            )

    mac_bold = bool(ttFont["head"].macStyle & MacStyle.BOLD)
    mac_italic = bool(ttFont["head"].macStyle & MacStyle.ITALIC)
    for flag, expected, label in [
        (bold_seen, mac_bold, "Bold"),
        (italic_seen, mac_italic, "Italic"),
    ]:
        if flag != expected:
            yield FAIL, Message(
                f"fsselection-macstyle-{label.lower()}",
                f"fsSelection {label} flag {flag}"
                f" does not match macStyle {expected} flag",
            )
