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

def test_check_kern_table():
  """ Is there a "kern" table declared in the font ? """
  from fontbakery.specifications.kern import com_google_fonts_check_kern_table as check

  # Our reference Mada Regular is known to be good
  # (does not have a 'kern' table):
  ttFont = TTFont(TEST_FILE("mada/Mada-Regular.ttf"))

  # So it must PASS the check:
  print ("Test PASS with a font without a 'kern' table...")
  status, message = list(check(ttFont))[-1]
  assert status == PASS

  # add a fake 'kern' table:
  ttFont["kern"] = "foo"

  # and make sure the check emits an INFO message:
  print ("Test INFO with a font containing a 'kern' table...")
  status, message = list(check(ttFont))[-1]
  assert status == INFO
