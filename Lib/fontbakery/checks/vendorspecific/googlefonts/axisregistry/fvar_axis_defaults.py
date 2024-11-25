from fontbakery.prelude import check, Message, FAIL
from fontbakery.checks.vendorspecific.googlefonts.utils import GFAxisRegistry


@check(
    id="googlefonts/axisregistry/fvar_axis_defaults",
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
def check_axisregistry_fvar_axis_defaults(ttFont):
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
