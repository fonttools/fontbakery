import os

from fontbakery.prelude import INFO, PASS, SKIP, WARN, Message, check


@check(
    id="com.google.fonts/check/superfamily/list",
    rationale="""
        This is a merely informative check that lists all sibling families
        detected by fontbakery.

        Only the fontfiles in these directories will be considered in
        superfamily-level checks.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1487",
)
def com_google_fonts_check_superfamily_list(superfamily):
    """List all superfamily filepaths"""
    for family in superfamily:
        yield INFO, Message("family-path", os.path.split(family[0])[0])


@check(
    id="com.google.fonts/check/superfamily/vertical_metrics",
    rationale="""
        We may want all fonts within a super-family (all sibling families) to have
        the same vertical metrics so their line spacing is consistent
        across the super-family.

        This is an experimental extended version of
        com.google.fonts/check/family/vertical_metrics and for now it will only
        result in WARNs.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1487",
)
def com_google_fonts_check_superfamily_vertical_metrics(superfamily_ttFonts):
    """
    Each font in set of sibling families must have the same set of vertical metrics
    values.
    """
    if len(superfamily_ttFonts) < 2:
        yield SKIP, "Sibling families were not detected."
        return

    warn = []
    vmetrics = {
        "sTypoAscender": {},
        "sTypoDescender": {},
        "sTypoLineGap": {},
        "usWinAscent": {},
        "usWinDescent": {},
        "ascent": {},
        "descent": {},
        "lineGap": {},
    }

    for family_ttFonts in superfamily_ttFonts:
        for ttFont in family_ttFonts:
            full_font_name = ttFont["name"].getBestFullName()
            vmetrics["sTypoAscender"][full_font_name] = ttFont["OS/2"].sTypoAscender
            vmetrics["sTypoDescender"][full_font_name] = ttFont["OS/2"].sTypoDescender
            vmetrics["sTypoLineGap"][full_font_name] = ttFont["OS/2"].sTypoLineGap
            vmetrics["usWinAscent"][full_font_name] = ttFont["OS/2"].usWinAscent
            vmetrics["usWinDescent"][full_font_name] = ttFont["OS/2"].usWinDescent
            vmetrics["ascent"][full_font_name] = ttFont["hhea"].ascent
            vmetrics["descent"][full_font_name] = ttFont["hhea"].descent
            vmetrics["lineGap"][full_font_name] = ttFont["hhea"].lineGap

    for k, v in vmetrics.items():
        metric_vals = set(vmetrics[k].values())
        if len(metric_vals) != 1:
            warn.append(k)

    if warn:
        for k in warn:
            s = ["{}: {}".format(k, v) for k, v in vmetrics[k].items()]
            s = "\n".join(s)
            yield WARN, Message(
                "superfamily-vertical-metrics",
                f"{k} is not the same across the super-family:\n{s}",
            )
    else:
        yield PASS, "Vertical metrics are the same across the super-family."
