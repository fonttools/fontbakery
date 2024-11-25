from fontbakery.prelude import check, Message, INFO, FAIL
from fontbakery.constants import PlatformID, WindowsEncodingID, WindowsLanguageID
from fontbakery.checks.vendorspecific.googlefonts.utils import GFAxisRegistry


@check(
    id="googlefonts/STAT/axisregistry",
    rationale="""
        Check that particle names and values on STAT table match the fallback names
        in each axis entry at the Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3022",
)
def check_STAT_axisregistry_names(ttFont):
    """
    Validate STAT particle names and values match the fallback names in GFAxisRegistry.
    """

    def normalize_name(name):
        return "".join(name.split(" "))

    format4_entries = False
    if "STAT" not in ttFont:
        yield FAIL, "Font is missing STAT table."
        return
    axis_value_array = ttFont["STAT"].table.AxisValueArray
    if not axis_value_array:
        yield FAIL, Message(
            "missing-axis-values", "STAT table is missing Axis Value Records"
        )
        return

    for axis_value in axis_value_array.AxisValue:
        if axis_value.Format == 4:
            coords = []
            for record in axis_value.AxisValueRecord:
                axis = ttFont["STAT"].table.DesignAxisRecord.Axis[record.AxisIndex]
                coords.append(f"{axis.AxisTag}:{record.Value}")
            coords = ", ".join(coords)

            name_entry = ttFont["name"].getName(
                axis_value.ValueNameID,
                PlatformID.WINDOWS,
                WindowsEncodingID.UNICODE_BMP,
                WindowsLanguageID.ENGLISH_USA,
            )
            format4_entries = True
            yield INFO, Message("format-4", f"'{name_entry.toUnicode()}' at ({coords})")
            continue

        axis = ttFont["STAT"].table.DesignAxisRecord.Axis[axis_value.AxisIndex]
        # If a family has a MORF axis, we allow users to define their own
        # axisValues for this axis.
        if axis.AxisTag == "MORF":
            continue
        if axis.AxisTag in GFAxisRegistry().keys():
            fallbacks = GFAxisRegistry()[axis.AxisTag].fallback
            fallbacks = {f.name: f.value for f in fallbacks}

            # Here we assume that it is enough to check for only the Windows,
            # English USA entry corresponding to a given nameID. It is up to other
            # checks to ensure all different platform/encoding entries
            # with a given nameID are consistent in the name table.
            name_entry = ttFont["name"].getName(
                axis_value.ValueNameID,
                PlatformID.WINDOWS,
                WindowsEncodingID.UNICODE_BMP,
                WindowsLanguageID.ENGLISH_USA,
            )

            # Here "name_entry" has the user-friendly name of the current AxisValue
            # We want to ensure that this string shows up as a "fallback" name
            # on the GF Axis Registry for this specific variation axis tag.
            name = normalize_name(name_entry.toUnicode())
            expected_names = [normalize_name(n) for n in fallbacks.keys()]
            if hasattr(axis_value, "Value"):  # Format 1 & 3
                is_value = axis_value.Value
            elif hasattr(axis_value, "NominalValue"):  # Format 2
                is_value = axis_value.NominalValue
            if name not in expected_names:
                expected_names = ", ".join(expected_names)
                yield FAIL, Message(
                    "invalid-name",
                    f"On the font variation axis '{axis.AxisTag}',"
                    f" the name '{name_entry.toUnicode()}'"
                    f" is not among the expected ones ({expected_names}) according"
                    " to the Google Fonts Axis Registry.",
                )
            elif is_value != fallbacks[name_entry.toUnicode()]:
                yield FAIL, Message(
                    "bad-coordinate",
                    f"Axis Value for '{axis.AxisTag}':'{name_entry.toUnicode()}' is"
                    f" expected to be '{fallbacks[name_entry.toUnicode()]}' but this"
                    f" font has '{name_entry.toUnicode()}'='{axis_value.Value}'.",
                )

    if format4_entries:
        yield INFO, Message(
            "format-4",
            "The GF Axis Registry does not currently contain fallback names"
            " for the combination of values for more than a single axis,"
            " which is what these 'format 4' entries are designed to describe,"
            " so this check will ignore them for now.",
        )
