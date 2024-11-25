from fontbakery.checks.vendorspecific.googlefonts.conditions import expected_font_names
from fontbakery.prelude import FAIL, WARN, Message, check
from fontbakery.utils import markdown_table


@check(
    id="googlefonts/fvar_instances",
    conditions=["is_variable_font", "not has_morf_axis"],
    rationale="""
        Check a font's fvar instance coordinates comply with our guidelines:
        https://googlefonts.github.io/gf-guide/variable.html#fvar-instances

        This check is skipped for fonts that have a Morph (MORF) axis
        since we allow users to define their own custom instances.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3800",
)
def check_fvar_instances(ttFont, ttFonts):
    """Check variable font instances"""
    expected_names = expected_font_names(ttFont, ttFonts)

    def get_instances(ttFont):
        name = ttFont["name"]
        fvar = ttFont["fvar"]
        res = {}
        for inst in fvar.instances:
            inst_name = name.getName(inst.subfamilyNameID, 3, 1, 0x409)
            if not inst_name:
                continue
            res[inst_name.toUnicode()] = inst.coordinates
        return res

    font_instances = get_instances(ttFont)
    expected_instances = get_instances(expected_names)
    table = []
    for name in set(font_instances.keys()) | set(expected_instances.keys()):
        row = {"Name": name}
        if name in font_instances:
            row["current"] = ", ".join(
                [f"{k}={v}" for k, v in font_instances[name].items()]
            )
        else:
            row["current"] = "N/A"
        if name in expected_instances:
            row["expected"] = ", ".join(
                [f"{k}={v}" for k, v in expected_instances[name].items()]
            )
        else:
            row["expected"] = "N/A"
        table.append(row)
    table = sorted(table, key=lambda k: str(k["expected"]))

    missing = set(expected_instances.keys()) - set(font_instances.keys())
    new = set(font_instances.keys()) - set(expected_instances.keys())
    same = set(font_instances.keys()) & set(expected_instances.keys())
    # check if instances have correct weight.
    if all("wght" in expected_instances[i] for i in expected_instances):
        wght_wrong = any(
            font_instances[i]["wght"] != expected_instances[i]["wght"] for i in same
        )
    else:
        wght_wrong = False

    md_table = markdown_table(table)
    if any([wght_wrong, missing, new]):
        hints = ""
        if missing:
            hints += "- Add missing instances\n"
        if new:
            hints += "- Delete additional instances\n"
        if wght_wrong:
            hints += "- wght coordinates are wrong for some instances"
        yield FAIL, Message(
            "bad-fvar-instances",
            f"fvar instances are incorrect:\n\n" f"{hints}\n\n{md_table}\n\n",
        )
    elif any(font_instances[i] != expected_instances[i] for i in same):
        yield WARN, Message(
            "suspicious-fvar-coords",
            f"fvar instance coordinates for non-wght axes are not the same as"
            f" the fvar defaults. This may be intentional so please check with"
            f" the font author:\n\n"
            f"{md_table}\n\n",
        )
