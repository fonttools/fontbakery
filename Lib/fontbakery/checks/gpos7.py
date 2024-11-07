from fontbakery.prelude import PASS, WARN, Message, check
from fontbakery.utils import iterate_lookup_list_with_extensions


@check(
    id="gpos7",
    conditions=["ttFont"],
    severity=9,
    rationale="""
        Versions of fonttools >=4.14.0 (19 August 2020) perform an optimisation on
        chained contextual lookups, expressing GSUB6 as GSUB5 and GPOS8 and GPOS7
        where possible (when there are no suffixes/prefixes for all rules in
        the lookup).

        However, makeotf has never generated these lookup types and they are rare
        in practice. Perhaps because of this, Mac's CoreText shaper does not correctly
        interpret GPOS7, meaning that these lookups will be ignored by the shaper,
        and fonts containing these lookups will have unintended positioning errors.

        To fix this warning, rebuild the font with a recent version of fonttools.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3643",
)
def check_gpos7(ttFont):
    """Ensure no GPOS7 lookups are present."""
    has_gpos7 = False

    def find_gpos7(lookup):
        nonlocal has_gpos7
        if lookup.LookupType == 7:
            has_gpos7 = True

    iterate_lookup_list_with_extensions(ttFont, "GPOS", find_gpos7)

    if not has_gpos7:
        yield PASS, "Font has no GPOS7 lookups"
        return

    yield WARN, Message(
        "has-gpos7", "Font contains a GPOS7 lookup which is not processed by macOS"
    )
