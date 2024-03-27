from fontbakery.callable import check, condition
from fontbakery.testable import Font
from fontbakery.status import WARN
from fontbakery.message import Message


@condition(Font)
def has_kerning_info(font):
    """A font has kerning info if it has a GPOS table containing at least one
    Pair Adjustment lookup (either directly or through an extension
    subtable)."""
    ttFont = font.ttFont
    if "GPOS" not in ttFont:
        return False

    if not ttFont["GPOS"].table.LookupList:
        return False

    for lookup in ttFont["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType == 2:  # type 2 = Pair Adjustment
            return True
        elif lookup.LookupType == 9:  # type 9 = Extension subtable
            for ext in lookup.SubTable:
                if ext.ExtensionLookupType == 2:  # type 2 = Pair Adjustment
                    return True


@check(
    id="com.google.fonts/check/gpos_kerning_info",
    proposal="legacy:check/063",
    rationale="""
            Well-designed fonts use kerning to improve the spacing between
            specific pairs of glyphs. This check ensures that the font has
            kerning information in the GPOS table. It can be ignored if the
            design or writing system does not require kerning.
       """,
)
def com_google_fonts_check_gpos_kerning_info(font):
    """Does GPOS table have kerning information?
    This check skips monospaced fonts as defined by post.isFixedPitch value
    """
    if font.ttFont["post"].isFixedPitch == 0 and not font.has_kerning_info:
        yield WARN, Message("lacks-kern-info", "GPOS table lacks kerning information.")
