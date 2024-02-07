from fontbakery.callable import check, condition
from fontbakery.status import PASS, WARN
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory  # noqa:F401 pylint:disable=W0611


@condition
def has_kerning_info(ttFont):
    """A font has kerning info if it has a GPOS table containing at least one
    Pair Adjustment lookup (either directly or through an extension
    subtable)."""
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


@check(id="com.google.fonts/check/gpos_kerning_info", proposal="legacy:check/063")
def com_google_fonts_check_gpos_kerning_info(ttFont):
    """Does GPOS table have kerning information?
    This check skips monospaced fonts as defined by post.isFixedPitch value
    """
    if ttFont["post"].isFixedPitch == 0 and not has_kerning_info(ttFont):
        yield WARN, Message("lacks-kern-info", "GPOS table lacks kerning information.")
    else:
        yield PASS, "GPOS table check for kerning information passed."
