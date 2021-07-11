from fontbakery.callable import check
from fontbakery.status import FAIL, PASS
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('is_variable_font',))
]

@check(
    id = 'com.google.fonts/check/varfont/stat_axis_record_for_each_axis',
    rationale = """
      According to the OpenType spec, there must be an Axis Record for every axis defined in the fvar table.

      https://docs.microsoft.com/en-us/typography/opentype/spec/stat#axis-records
    """,
    conditions = ['is_variable_font'],
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3017'
)
def com_google_fonts_check_varfont_stat_axis_record_for_each_axis(ttFont):
    """ All fvar axes have a correspondent Axis Record on STAT table? """
    fvar_axes = set(a.axisTag for a in ttFont['fvar'].axes)
    stat_axes = set(a.AxisTag for a in ttFont['STAT'].table.DesignAxisRecord.Axis)
    missing_axes = fvar_axes - stat_axes
    if len(missing_axes) > 0:
        yield FAIL,\
              Message("missing-axis-records",
                      f"STAT table is missing Axis Records for"
                      f" the following axes: {missing_axes}")
    else:
        yield PASS, "STAT table has all necessary Axis Records"

