from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import condition

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
