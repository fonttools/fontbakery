from fontbakery.utils import TEST_FILE
from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

check_statuses = (ERROR, FAIL, SKIP, PASS, WARN, INFO, DEBUG)

from fontTools.ttLib import TTFont

def test_check_gpos_kerning_info():
  """ Does GPOS table have kerning information? """
  from fontbakery.profiles.gpos import com_google_fonts_check_gpos_kerning_info as check

  # Our reference Mada Regular is known to have kerning-info
  # exclusively on an extension subtable
  # (lookup type = 9 / ext-type = 2):
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  print ("Test PASS with a font that has got kerning info...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # delete all Pair Adjustment lookups:
  while True:
    found = False
    for l, lookup in enumerate(ttFont["GPOS"].table.LookupList.Lookup):
      #if lookup.LookupType == 2:  # type 2 = Pair Adjustment
      #  del ttFont["GPOS"].table.LookupList.Lookup[l]
      #  found = True
      if lookup.LookupType == 9:  # type 9 = Extension subtable
        for e, ext in enumerate(lookup.SubTable):
          if ext.ExtensionLookupType == 2:  # type 2 = Pair Adjustment
            del ttFont["GPOS"].table.LookupList.Lookup[l].SubTable[e]
            found = True
    if not found:
      break

  print ("Test WARN with a font lacking kerning info...")
  status, message = list(check(ttFont))[-1]
  assert status == WARN and message.code == "lacks-kern-info"

  # setup a fake type=2 Pair Adjustment lookup
  ttFont["GPOS"].table.LookupList.Lookup[0].LookupType = 2
  # and make sure the check emits a PASS result:
  print ("Test PASS with kerning info on a type=2 lookup...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # remove the GPOS table and make sure to get a WARN:
  del ttFont["GPOS"]
  print ("Test WARN with a font lacking a GPOS table...")
  status, message = list(check(ttFont))[-1]
  assert status == WARN and message.code == "lacks-kern-info"
