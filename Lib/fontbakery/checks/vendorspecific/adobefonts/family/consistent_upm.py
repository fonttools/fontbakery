from fontbakery.prelude import check, Message, FAIL


@check(
    id="adobefonts/family/consistent_upm",
    rationale="""
        While not required by the OpenType spec, we (Adobe) expect that a group
        of fonts designed & produced as a family have consistent units per em.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/2372",
)
def check_family_consistent_upm(ttFonts):
    """Fonts have consistent Units Per Em?"""
    upm_set = set()
    for ttFont in ttFonts:
        upm_set.add(ttFont["head"].unitsPerEm)
    if len(upm_set) > 1:
        yield FAIL, Message(
            "inconsistent-upem",
            f"Fonts have different units per em: {sorted(upm_set)}.",
        )
