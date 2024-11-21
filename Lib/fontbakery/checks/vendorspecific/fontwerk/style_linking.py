from fontbakery.prelude import check, FAIL, Message
from fontbakery.constants import FsSelection, MacStyle


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
