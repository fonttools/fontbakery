from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from fontbakery.callable import condition
from fontbakery.checkrunner import SKIP

# TODO: Design special case handling for whitelists/blacklists
# https://github.com/googlefonts/fontbakery/issues/1540
@condition
def whitelist_librebarcode(font):
  font_filenames = [
    "LibreBarcode39-Regular.ttf",
    "LibreBarcode39Text-Regular.ttf",
    "LibreBarcode128-Regular.ttf",
    "LibreBarcode128Text-Regular.ttf"
  ]
  for font_filename in font_filenames:
    if font_filename in font:
      return True


@condition
def style(font):
  """Determine font style from canonical filename."""
  from fontbakery.constants import STYLE_NAMES
  filename = os.path.split(font)[-1]
  if '-' in filename:
    stylename = os.path.splitext(filename)[0].split('-')[1]
    if stylename in [name.replace(' ', '') for name in STYLE_NAMES]:
      return stylename
