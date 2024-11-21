from fontbakery.prelude import check, condition, Message, PASS, FAIL
from fontbakery.testable import CheckRunContext


@condition(CheckRunContext)
def vmetrics(collection):
    from fontbakery.utils import get_bounding_box

    v_metrics = {"ymin": 0, "ymax": 0}
    for ttFont in collection.ttFonts:
        font_ymin, font_ymax = get_bounding_box(ttFont)
        v_metrics["ymin"] = min(font_ymin, v_metrics["ymin"])
        v_metrics["ymax"] = max(font_ymax, v_metrics["ymax"])
    return v_metrics


@check(
    id="family/win_ascent_and_descent",
    conditions=["vmetrics", "not is_cjk_font"],
    rationale="""
        A font's winAscent and winDescent values should be greater than or equal to
        the head table's yMax, abs(yMin) values. If they are less than these values,
        clipping can occur on Windows platforms
        (https://github.com/RedHatBrand/Overpass/issues/33).

        If the font includes tall/deep writing systems such as Arabic or Devanagari,
        the winAscent and winDescent can be greater than the yMax and absolute yMin
        values to accommodate vowel marks.

        When the 'win' Metrics are significantly greater than the UPM, the linespacing
        can appear too loose. To counteract this, enabling the OS/2 fsSelection
        bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 'typo' values
        instead. This means the font developer can control the linespacing with
        the 'typo' values, whilst avoiding clipping by setting the 'win' values to
        values greater than the yMax and absolute yMin.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_family_win_ascent_and_descent(ttFont, vmetrics):
    """Checking OS/2 usWinAscent & usWinDescent."""

    # NOTE:
    # This check works on a single font file as well as on a group of font files.
    # Even though one of this check's inputs is 'ttFont' (whereas other family-wide
    # checks use 'ttFonts') the other input parameter, 'vmetrics', will collect vertical
    # metrics values for all the font files provided in the command line. This means
    # that running the check may yield more or less results depending on the set of font
    # files that is provided in the command line. This behaviour is NOT a bug.
    # For example, compare the results of these two commands:
    #   fontbakery check-universal -c ascent_and_descent data/test/mada/Mada-Regular.ttf
    #   fontbakery check-universal -c ascent_and_descent data/test/mada/*.ttf
    #
    # The second command will yield more FAIL results for each font. This happens
    # because the check does a family-wide validation of the vertical metrics, instead
    # of a single font validation.

    if "OS/2" not in ttFont:
        yield FAIL, Message("lacks-OS/2", "Font file lacks OS/2 table")
        return

    failed = False
    os2_table = ttFont["OS/2"]
    win_ascent = os2_table.usWinAscent
    win_descent = os2_table.usWinDescent
    y_max = vmetrics["ymax"]
    y_min = vmetrics["ymin"]

    # OS/2 usWinAscent:
    if win_ascent < y_max:
        failed = True
        yield FAIL, Message(
            "ascent",
            f"OS/2.usWinAscent value should be equal or greater than {y_max},"
            f" but got {win_ascent} instead",
        )
    if win_ascent > y_max * 2:
        failed = True
        yield FAIL, Message(
            "ascent",
            f"OS/2.usWinAscent value {win_ascent} is too large."
            f" It should be less than double the yMax. Current yMax value is {y_max}",
        )
    # OS/2 usWinDescent:
    if win_descent < abs(y_min):
        failed = True
        yield FAIL, Message(
            "descent",
            f"OS/2.usWinDescent value should be equal or greater than {abs(y_min)},"
            f" but got {win_descent} instead",
        )

    if win_descent > abs(y_min) * 2:
        failed = True
        yield FAIL, Message(
            "descent",
            f"OS/2.usWinDescent value {win_descent} is too large."
            " It should be less than double the yMin."
            f" Current absolute yMin value is {abs(y_min)}",
        )
    if not failed:
        yield PASS, "OS/2 usWinAscent & usWinDescent values look good!"
