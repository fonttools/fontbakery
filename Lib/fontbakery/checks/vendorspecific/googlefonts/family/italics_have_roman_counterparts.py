import os

from fontbakery.prelude import check, Message, WARN, FAIL


@check(
    id="googlefonts/family/italics_have_roman_counterparts",
    rationale="""
        For each font family on Google Fonts, every Italic style must have
        a Roman sibling.

        This kind of problem was first observed at [1] where the Bold style was
        missing but BoldItalic was included.

        [1] https://github.com/google/fonts/pull/1482
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/1733",
)
def check_family_italics_have_roman_counterparts(fonts, config):
    """Ensure Italic styles have Roman counterparts."""

    filenames = [f.file for f in fonts]
    italics = [
        f.file
        for f in fonts
        if "Italic" in f.file and f.file.find("-") < f.file.find("Italic")
    ]
    missing_roman = []
    for italic in italics:
        if (
            "-" not in os.path.basename(italic)
            or len(os.path.basename(italic).split("-")[-1].split(".")) != 2
        ):
            yield WARN, Message(
                "bad-filename", f"Filename seems to be incorrect: '{italic}'"
            )

        style_from_filename = os.path.basename(italic).split("-")[-1].split(".")[0]
        is_varfont = "[" in style_from_filename

        # to remove the axes syntax used on variable-font filenames:
        if is_varfont:
            style_from_filename = style_from_filename.split("[")[0]

        if style_from_filename == "Italic":
            if is_varfont:
                # "Familyname-Italic[wght,wdth].ttf" => "Familyname[wght,wdth].ttf"
                roman_counterpart = italic.replace("-Italic", "")
            else:
                # "Familyname-Italic.ttf" => "Familyname-Regular.ttf"
                roman_counterpart = italic.replace("Italic", "Regular")
        else:
            # "Familyname-BoldItalic[wght,wdth].ttf" => "Familyname-Bold[wght,wdth].ttf"
            roman_counterpart = italic.replace("Italic", "")

        if roman_counterpart not in filenames:
            missing_roman.append(italic)

    if missing_roman:
        from fontbakery.utils import pretty_print_list

        missing_roman = pretty_print_list(config, missing_roman)
        yield FAIL, Message(
            "missing-roman", f"Italics missing a Roman counterpart: {missing_roman}"
        )
