import os
from fontbakery.prelude import check, Message, PASS, FAIL


@check(
    id="family/vertical_metrics",
    rationale="""
        We want all fonts within a family to have the same vertical metrics so
        their line spacing is consistent across the family.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1487",
)
def check_family_vertical_metrics(ttFonts):
    """Each font in a family must have the same set of vertical metrics values."""
    failed = []
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

    missing_tables = False
    for ttFont in ttFonts:
        filename = os.path.basename(ttFont.reader.file.name)
        if "OS/2" not in ttFont:
            missing_tables = True
            yield FAIL, Message("lacks-OS/2", f"{filename} lacks an 'OS/2' table.")
            continue

        if "hhea" not in ttFont:
            missing_tables = True
            yield FAIL, Message("lacks-hhea", f"{filename} lacks a 'hhea' table.")
            continue

        full_font_name = ttFont["name"].getBestFullName()
        vmetrics["sTypoAscender"][full_font_name] = ttFont["OS/2"].sTypoAscender
        vmetrics["sTypoDescender"][full_font_name] = ttFont["OS/2"].sTypoDescender
        vmetrics["sTypoLineGap"][full_font_name] = ttFont["OS/2"].sTypoLineGap
        vmetrics["usWinAscent"][full_font_name] = ttFont["OS/2"].usWinAscent
        vmetrics["usWinDescent"][full_font_name] = ttFont["OS/2"].usWinDescent
        vmetrics["ascent"][full_font_name] = ttFont["hhea"].ascent
        vmetrics["descent"][full_font_name] = ttFont["hhea"].descent
        vmetrics["lineGap"][full_font_name] = ttFont["hhea"].lineGap

    if not missing_tables:
        # It is important to first ensure all font files have OS/2 and hhea tables
        # before performing the rest of the check routine.

        for k, v in vmetrics.items():
            metric_vals = set(vmetrics[k].values())
            if len(metric_vals) != 1:
                failed.append(k)

        if failed:
            for k in failed:
                s = ["{}: {}".format(k, v) for k, v in vmetrics[k].items()]
                s = "\n".join(s)
                yield FAIL, Message(
                    f"{k}-mismatch", f"{k} is not the same across the family:\n{s}"
                )
        else:
            yield PASS, "Vertical metrics are the same across the family."
