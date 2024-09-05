"""
Checks for Fontwerk <https://fontwerk.com/>
"""

from fontbakery.prelude import check, FAIL, INFO, Message
from fontbakery.constants import FsSelection, MacStyle


@check(
    id="fontwerk/vendor_id",
    rationale="""
        Vendor ID must be WERK for Fontwerk fonts.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3579",
)
def check_vendor_id(ttFont):
    """Checking OS/2 achVendID."""

    vendor_id = ttFont["OS/2"].achVendID
    if vendor_id != "WERK":
        yield FAIL, Message(
            "bad-vendor-id", f"OS/2 VendorID is '{vendor_id}', but should be 'WERK'."
        )


@check(
    id="fontwerk/names_match_default_fvar",
    rationale="""
        Check if the font names match default fvar instance name.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/pull/3698",
)
def check_names_match_default_fvar(ttFont):
    """Checking if names match default fvar instance name."""
    from fontbakery.constants import NameID

    default_axis_values = {
        axis.axisTag: axis.defaultValue for axis in ttFont["fvar"].axes
    }
    default_name_id = None
    for instance in ttFont["fvar"].instances:
        if instance.coordinates == default_axis_values:
            default_name_id = instance.subfamilyNameID
            break

    if default_name_id is None:
        yield FAIL, Message(
            "missing-default-name-id", "fvar is missing a default instance name ID."
        )
        return

    fam_name = ttFont["name"].getBestFamilyName()
    subfam_name = ttFont["name"].getDebugName(default_name_id)

    if subfam_name is None:
        yield FAIL, Message(
            "missing-name-id",
            f"Name ID {default_name_id} stored in"
            f" fvar instance is missing in name table.",
        )
        return

    default_name = f"{fam_name} {subfam_name}"

    # check if default_name match family + subfamily name
    for fam_id, subfam_id in [
        (NameID.WWS_FAMILY_NAME, NameID.WWS_SUBFAMILY_NAME),
        (NameID.TYPOGRAPHIC_FAMILY_NAME, NameID.TYPOGRAPHIC_SUBFAMILY_NAME),
        (NameID.FONT_FAMILY_NAME, NameID.FONT_SUBFAMILY_NAME),
    ]:
        name_fam = ttFont["name"].getDebugName(fam_id)
        name_subfam = ttFont["name"].getDebugName(subfam_id)

        if (fam_id, subfam_id) in [
            (NameID.WWS_FAMILY_NAME, NameID.WWS_SUBFAMILY_NAME),
            (NameID.TYPOGRAPHIC_FAMILY_NAME, NameID.TYPOGRAPHIC_SUBFAMILY_NAME),
        ]:
            if [name_fam, name_subfam] == [None, None]:
                yield INFO, Message(
                    "missing-name-ids",
                    f"It's not a requirement that a font has "
                    f"to have these name IDs {fam_id} and {subfam_id}.",
                )
                continue

        if name_fam is None:
            yield FAIL, Message("missing-name-id", "Missing name ID {fam_id}.")
        elif name_subfam is None:
            yield FAIL, Message("missing-name-id", "Missing name ID {subfam_id}.")
        else:
            possible_names = [f"{name_fam} {name_subfam}"]
            if name_subfam.lower() == "regular":
                possible_names.append(name_fam)

            if default_name not in possible_names:
                yield FAIL, Message(
                    "bad-name",
                    f"Name {possible_names} does not match fvar"
                    f" default name '{default_name}'",
                )


@check(
    id="fontwerk/style_linking",
    rationale="""
        Look for possible style linking issues.
    """,
    proposal="https://github.com/googlefonts/noto-fonts/issues/2269",
)
def check_style_linking(ttFont, font):
    """Checking style linking entries"""

    errs = []
    if font.is_bold:
        if not (ttFont["OS/2"].fsSelection & FsSelection.BOLD):
            errs.append("OS/2 fsSelection flag should be (most likely) 'Bold'.")
        if not (ttFont["head"].macStyle & MacStyle.BOLD):
            errs.append("head macStyle flag should be (most likely) 'Bold'.")
        if ttFont["name"].getDebugName(2) not in ("Bold", "Bold Italic"):
            name_id_2_should_be = "Bold"
            if font.is_italic:
                name_id_2_should_be = "Bold Italic"
            errs.append(f"name ID should be (most likely) '{name_id_2_should_be}'.")

    if font.is_italic:
        if "post" in ttFont and not ttFont["post"].italicAngle:
            errs.append(
                "post talbe italic angle should be (most likely) different to 0."
            )
        if not (ttFont["OS/2"].fsSelection & FsSelection.ITALIC):
            errs.append("OS/2 fsSelection flag should be (most likely) 'Italic'.")
        if not (ttFont["head"].macStyle & MacStyle.ITALIC):
            errs.append("head macStyle flag should be (most likely) 'Italic'.")
        if ttFont["name"].getDebugName(2) not in ("Italic", "Bold Italic"):
            name_id_2_should_be = "Italic"
            if font.is_bold:
                name_id_2_should_be = "Bold Italic"
            errs.append(f"name ID should be (most likely) '{name_id_2_should_be}'.")

    for err in errs:
        yield FAIL, Message("style-linking-issue", err)
