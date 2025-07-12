from fontbakery.constants import NameID
from fontbakery.prelude import check, FAIL, Message
from fontbakery.utils import get_family_name, get_subfamily_name


def _check_name_length_req(family_name, subfamily_name):
    if family_name is None:
        yield FAIL, Message("missing-name-id", "Name ID 1 (family) missing")
    if subfamily_name is None:
        yield FAIL, Message("missing-name-id", "Name ID 2 (sub family) missing")

    logfont = (
        family_name
        if subfamily_name in ("Regular", "Bold", "Italic", "Bold Italic")
        else " ".join([family_name, subfamily_name])
    )

    if len(logfont) > 31:
        yield FAIL, Message(
            "long-name",
            f"Family + subfamily name, '{logfont}', is too long: "
            f"{len(logfont)} characters; must be 31 or less",
        )


@check(
    id="name_length_req",
    rationale="""
        For Office, family and subfamily names must be 31 characters or less total
        to fit in a LOGFONT.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_name_length_req(ttFont):
    """Maximum allowed length for family and subfamily names."""
    family_name = get_family_name(ttFont)
    subfamily_name = get_subfamily_name(ttFont)
    yield from _check_name_length_req(family_name, subfamily_name)


def resolve_stat_names(vf, coordinates):
    """
    Returns a dictionary of names & axis order, indexed by axis tag, for an
    instance in the given font at the given coordinates.

    e.g. result['wght']: ('Regular', 0)
    """
    stat_table = vf["STAT"].table
    result = {}

    for avr in stat_table.AxisValueArray.AxisValue:
        axis_tag = stat_table.DesignAxisRecord.Axis[avr.AxisIndex].AxisTag
        if (
            axis_tag in coordinates
            and (
                (
                    avr.Format == 2
                    and avr.RangeMinValue <= coordinates[axis_tag] <= avr.RangeMaxValue
                )
                or (avr.Format in (1, 3) and avr.Value == coordinates[axis_tag])
            )
        ) or (axis_tag not in coordinates):
            if avr.Flags & 0x2 == 0:
                name = vf["name"].getDebugName(avr.ValueNameID)
                axis_order = stat_table.DesignAxisRecord.Axis[
                    avr.AxisIndex
                ].AxisOrdering
                result[axis_tag] = (name, axis_order)

    return result


RBIZ_AXES = ["wght", "ital"]


def compute_rbiz_names(family, stat_names, rbiz_axes):
    # Name IDs 1 & 2 in a RBIZ model
    rbiz_family_names = [
        n
        for axis, (n, _) in sorted(stat_names.items(), key=lambda x: x[1][1])
        if axis not in rbiz_axes
    ]
    rbiz_family = " ".join([f"{family}", *rbiz_family_names])
    rbiz_subfamily_names = [
        stat_names[axis] for axis in rbiz_axes if axis in stat_names
    ]
    rbiz_subfamily = " ".join(
        [n for n, _ in sorted(rbiz_subfamily_names, key=lambda x: x[1])]
    )
    if rbiz_subfamily == "":
        rbiz_subfamily = "Regular"
    return (rbiz_family, rbiz_subfamily)


def names_from_stat(vf, coordinates):
    """
    Returns family and subfamily names generated from the STAT and name tables, for an instance
    at the given coordinates.
    """
    stat_names = resolve_stat_names(vf, coordinates)

    # Find any implicit style names in ID 1 by removing ID 16 and any of the
    # default instance style names. E.g. if ID 1 is "Bahnschrift Rounded Light",
    # and ID 16 is "Bahnschrift", find "Rounded".
    id1 = vf["name"].getDebugName(NameID.FONT_FAMILY_NAME)
    id16 = vf["name"].getDebugName(NameID.TYPOGRAPHIC_FAMILY_NAME)
    if id1 and id16 and id1.startswith(id16) and id1 != id16:
        id1_names = id1[len(id16) + 1 :].split(" ")
        default_inst_coords = {
            axis.axisTag: axis.defaultValue for axis in vf["fvar"].axes
        }
        default_stat_names = resolve_stat_names(vf, default_inst_coords)
        default_stat_names = [n for n, _ in sorted(default_stat_names.values())]
        remaining_names = [n for n in id1_names if n not in default_stat_names]
        # Update axis ordering in stat_names
        for axis_tag, (name, ordering) in stat_names.items():
            stat_names[axis_tag] = (name, ordering + len(remaining_names))
        # Add the names from ID 1
        stat_names.update({f"X{i:<3}": (n, i) for i, n in enumerate(remaining_names)})

    family = vf["name"].getDebugName(NameID.TYPOGRAPHIC_FAMILY_NAME)
    if family is None:
        family = vf["name"].getDebugName(NameID.FONT_FAMILY_NAME)

    rbiz_axes = list(RBIZ_AXES)
    if "wght" in coordinates and coordinates["wght"] not in (400, 700):
        rbiz_axes = [x for x in rbiz_axes if x != "wght"]

    rbiz_family, rbiz_subfamily = compute_rbiz_names(family, stat_names, rbiz_axes)
    return rbiz_family, rbiz_subfamily


@check(
    id="instances_name_length_req",
    conditions=["is_variable_font"],
    rationale="""
        For Office, instance family and subfamily names must be 31 characters or less total
        to fit in a LOGFONT.
    """,
)
def instances_name_length_req(ttFont):
    """Maximum allowed length for instance family and subfamily names."""
    fvar = ttFont["fvar"]
    for instance in fvar.instances:
        family_name, subfamily_name = names_from_stat(ttFont, instance.coordinates)
        yield from _check_name_length_req(family_name, subfamily_name)
