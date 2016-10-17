#!/usr/bin/env python

check_ttf = __import__("fontbakery-check-ttf").fontbakery_check_ttf

config = {
  'verbose': True,
  'ghm': True,
  'json': False,
  'error': False,
  'autofix': False,
  'filepaths': ['/home/felipe/devel/github_felipesanches/Arsenal/fonts/ttf/*.ttf']
}

check_ttf(config)

