from fontbakery.prelude import check, Message, FAIL
from fontbakery.utils import bullet_list


@check(
    id="varfont/instances_in_order",
    rationale="""
        Ensure that the fvar table instances are in ascending order of weight.
        Some software, such as Canva, displays the instances in the order they
        are defined in the fvar table, which can lead to confusion if the
        instances are not in order of weight.
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3334",
    severity=2,  # It only affects a few applications
    conditions=["has_wght_axis"],
)
def check_varfont_instances_in_order(ttFont, config):
    """Ensure the font's instances are in the correct order."""

    coords = [i.coordinates for i in ttFont["fvar"].instances]
    # Partition into sub-lists based on the other axes values.
    # e.g. "Thin Regular", "Bold Regular", "Thin Condensed", "Bold Condensed"
    # becomes [ ["Thin Regular", "Bold Regular"], ["Thin Condensed", "Bold Condensed"] ]
    sublists = [[]]
    last_non_wght = {}
    for coord in coords:
        non_wght = {k: v for k, v in coord.items() if k != "wght"}
        if non_wght != last_non_wght:
            sublists.append([])
            last_non_wght = non_wght
        sublists[-1].append(coord)

    for lst in sublists:
        wght_values = [i["wght"] for i in lst]
        if wght_values != sorted(wght_values):
            yield FAIL, Message(
                "instances-not-in-order",
                "The fvar table instances are not in ascending order of weight:\n"
                + bullet_list(config, lst),
            )
