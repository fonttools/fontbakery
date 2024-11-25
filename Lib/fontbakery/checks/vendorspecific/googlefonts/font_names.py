from fontbakery.checks.vendorspecific.googlefonts.conditions import expected_font_names
from fontbakery.prelude import check, Message, FAIL, WARN
from fontbakery.constants import (
    NameID,
)
from fontbakery.utils import markdown_table


@check(
    id="googlefonts/font_names",
    rationale="""
        Google Fonts has several rules which need to be adhered to when
        setting a font's name table. Please read:
        https://googlefonts.github.io/gf-guide/statics.html#supported-styles
        https://googlefonts.github.io/gf-guide/statics.html#style-linking
        https://googlefonts.github.io/gf-guide/statics.html#unsupported-styles
        https://googlefonts.github.io/gf-guide/statics.html#single-weight-families
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def check_font_names(ttFont, ttFonts):
    """Check font names are correct"""
    if "fvar" in ttFont and "MORF" in [a.axisTag for a in ttFont["fvar"].axes]:
        yield WARN, Message(
            "morf-axis",
            "Font has a Morph axis. This check only works on fonts that "
            "have a wght axis. Since users can define their own stylenames "
            "for Morph families, please manually check that the family works "
            "on major platforms. You can use Agu Display as a reference.",
        )
        return
    expected_names = expected_font_names(ttFont, ttFonts)

    def style_names(nametable):
        res = {}
        for nameID in (
            NameID.FONT_FAMILY_NAME,
            NameID.FONT_SUBFAMILY_NAME,
            NameID.FULL_FONT_NAME,
            NameID.POSTSCRIPT_NAME,
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
        ):
            rec = nametable.getName(nameID, 3, 1, 0x409)
            if rec:
                res[nameID] = rec.toUnicode()
        return res

    font_names = style_names(ttFont["name"])
    expected_names = style_names(expected_names["name"])

    name_ids = {
        NameID.FONT_FAMILY_NAME: "Family Name",
        NameID.FONT_SUBFAMILY_NAME: "Subfamily Name",
        NameID.FULL_FONT_NAME: "Full Name",
        NameID.POSTSCRIPT_NAME: "Postscript Name",
        NameID.TYPOGRAPHIC_FAMILY_NAME: "Typographic Family Name",
        NameID.TYPOGRAPHIC_SUBFAMILY_NAME: "Typographic Subfamily Name",
    }
    table = []
    for nameID in set(font_names.keys()) | set(expected_names.keys()):
        id_name = name_ids[nameID]
        row = {"nameID": id_name}
        if nameID in font_names:
            row["current"] = font_names[nameID]
        else:
            row["current"] = "N/A"
        if nameID in expected_names:
            row["expected"] = expected_names[nameID]
        else:
            row["expected"] = "N/A"
        if row["current"] != row["expected"]:
            row["current"] = "**" + row["current"] + "**"
            row["expected"] = "**" + row["expected"] + "**"
        table.append(row)

    new_names = set(font_names) - set(expected_names)
    missing_names = set(expected_names) - set(font_names)
    same_names = set(font_names) & set(expected_names)

    md_table = markdown_table(table)

    passed = True
    if new_names or missing_names:
        passed = False

    for nameID in same_names:
        if nameID == NameID.FULL_FONT_NAME and all(
            [
                " Regular" in expected_names[nameID],
                font_names[nameID] == expected_names[nameID].replace(" Regular", ""),
            ]
        ):
            yield WARN, Message("lacks-regular", "Regular missing from full name")
        elif font_names[nameID] != expected_names[nameID]:
            passed = False

    if not passed:
        yield FAIL, Message("bad-names", f"Font names are incorrect:\n\n{md_table}")
