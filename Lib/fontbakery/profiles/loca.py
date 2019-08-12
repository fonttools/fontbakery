from fontbakery.callable import check
from fontbakery.checkrunner import PASS, FAIL
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = (
    ('.', ('shared_conditions', )),
)

@check(
  id = 'com.google.fonts/check/loca/maxp_num_glyphs',
  conditions = ['is_ttf']
)
def com_google_fonts_check_loca_maxp_num_glyphs(ttFont):
  """Does the number of glyphs in the loca table match the maxp table?"""
  if len(ttFont['loca']) < (ttFont['maxp'].numGlyphs + 1):
    yield FAIL,\
          Message("corrupt",
                  'Corrupt "loca" table,'
                  ' or wrong numGlyphs in "maxp" table.')
  else:
    yield PASS, "'loca' table matches numGlyphs in 'maxp' table."
