from functools import lru_cache
from fontbakery.prelude import check, Message, INFO, FAIL
from fontbakery.constants import PlatformID, WindowsEncodingID, WindowsLanguageID


@lru_cache(maxsize=1)
def GFAxisRegistry():
    from axisregistry import AxisRegistry

    return AxisRegistry()


@check(
    id="com.google.fonts/check/metadata/gf_axisregistry_bounds",
    rationale="""
        Each axis range in a METADATA.pb file must be registered, and within the bounds
        of the axis definition in the Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry
    """,
    conditions=["is_variable_font", "family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3010",
)
def com_google_fonts_check_gf_axisregistry_bounds(family_metadata):
    """Validate METADATA.pb axes values are within gf_axisregistry bounds."""
    for axis in family_metadata.axes:
        if axis.tag in GFAxisRegistry().keys():
            expected = GFAxisRegistry()[axis.tag]
            if (
                axis.min_value < expected.min_value
                or axis.max_value > expected.max_value
            ):
                yield FAIL, Message(
                    "bad-axis-range",
                    f"The range in the font variation axis"
                    f" '{axis.tag}' ({expected.display_name}"
                    f" min:{axis.min_value} max:{axis.max_value})"
                    f" does not comply with the expected maximum range,"
                    f" as defined on Google Fonts Axis Registry"
                    f" (min:{expected.min_value} max:{expected.max_value}).",
                )


@check(
    id="com.google.fonts/check/metadata/gf_axisregistry_valid_tags",
    rationale="""
        Ensure all axes in a METADATA.pb file are registered in the
        Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry

        Why does Google Fonts have its own Axis Registry?

        We support a superset of the OpenType axis registry axis set, and use
        additional metadata for each axis. Axes present in a font file but not in this
        registry will not function via our API. No variable font is expected to
        support all of the axes here.

        Any font foundry or distributor library that offers variable fonts has a
        implicit, latent, de-facto axis registry, which can be extracted by scanning
        the library for axes' tags, labels, and min/def/max values. While in 2016
        Microsoft originally offered to include more axes in the OpenType 1.8
        specification (github.com/microsoft/OpenTypeDesignVariationAxisTags), as of
        August 2020, this effort has stalled. We hope more foundries and distributors
        will publish documents like this that make their axes explicit, to encourage
        of adoption of variable fonts throughout the industry, and provide source
        material for a future update to the OpenType specification's axis registry.
    """,
    conditions=["is_variable_font", "family_metadata"],
    proposal="https://github.com/fonttools/fontbakery/issues/3022",
)
def com_google_fonts_check_gf_axisregistry_valid_tags(family_metadata):
    """Validate METADATA.pb axes tags are defined in gf_axisregistry."""
    for axis in family_metadata.axes:
        if axis.tag not in GFAxisRegistry().keys():
            yield FAIL, Message(
                "bad-axis-tag",
                f"The font variation axis '{axis.tag}'"
                f" is not yet registered on Google Fonts Axis Registry.",
            )


@check(
    id="com.google.fonts/check/gf_axisregistry/fvar_axis_defaults",
    rationale="""
        Check that axis defaults have a corresponding fallback name registered at the
        Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry

        This is necessary for the following reasons:

        To get ZIP files downloads on Google Fonts to be accurate — otherwise the
        chosen default font is not generated. The Newsreader family, for instance, has
        a default value on the 'opsz' axis of 16pt. If 16pt was not a registered
        fallback position, then the ZIP file would instead include another position
        as default (such as 14pt).

        For the Variable fonts to display the correct location on the specimen page.

        For VF with no weight axis to be displayed at all. For instance, Ballet, which
        has no weight axis, was not appearing in sandbox because default position on
        'opsz' axis was 16pt, and it was not yet a registered fallback positon.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3141",
)
def com_google_fonts_check_gf_axisregistry_fvar_axis_defaults(ttFont):
    """
    Validate defaults on fvar table match registered fallback names in GFAxisRegistry.
    """

    for axis in ttFont["fvar"].axes:
        if axis.axisTag not in GFAxisRegistry():
            continue
        fallbacks = GFAxisRegistry()[axis.axisTag].fallback
        if axis.defaultValue not in [f.value for f in fallbacks]:
            yield FAIL, Message(
                "not-registered",
                f"The defaul value {axis.axisTag}:{axis.defaultValue} is not registered"
                " as an axis fallback name on the Google Axis Registry.\n\tYou should"
                " consider suggesting the addition of this value to the registry"
                " or adopted one of the existing fallback names for this axis:\n"
                f"\t{fallbacks}",
            )


@check(
    id="com.google.fonts/check/STAT/gf_axisregistry",
    rationale="""
        Check that particle names and values on STAT table match the fallback names
        in each axis entry at the Google Fonts Axis Registry, available at
        https://github.com/google/fonts/tree/main/axisregistry
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/3022",
)
def com_google_fonts_check_STAT_gf_axisregistry_names(ttFont):
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
