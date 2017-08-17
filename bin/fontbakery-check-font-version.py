#!/usr/bin/env python
"""
fontbakery-check-font-version.py:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the version number of a family hosted on fonts.google.com.

`fontbakery check-font-version "Roboto"`


Comparison against a local family can be made using the -lc argument:

`fontbakery check-font-version "Roboto" -lc [/dir/Roboto-Regular.ttf, ...]`


Comparison against a url containing a zipped family can be made using
the -wc argument:

`fontbakery check-font-version "Roboto" -wc=http://roboto.com/roboto.zip`

"""
from __future__ import print_function
from argparse import ArgumentParser
from fontTools.ttLib import TTFont
from ntpath import basename

from fontbakery.utils import (
  download_family_from_Google_Fonts,
  download_zip,
  fonts_from_zip,
  parse_version_head,
)

def main():
  parser = ArgumentParser(description=__doc__)
  parser.add_argument('family',
            help='Name of font family')
  parser.add_argument('-wc', '--web-compare',
                      help='Compare against a web url .zip family')
  parser.add_argument('-lc', '--local-compare', nargs='+',
                      help='Compare against a set of local ttfs')
  args = parser.parse_args()

  google_family_zip = download_family_from_Google_Fonts(args.family)
  google_family_fonts = [f[1] for f in fonts_from_zip(google_family_zip)]
  google_family_version = parse_version_head(google_family_fonts)

  if args.web_compare:
    if args.web_compare.endswith('.zip'):
      web_family_zip = download_zip(args.web_compare)
      web_family = fonts_from_zip(web_family_zip)
      web_family_fonts = [f[1] for f in web_family]
      web_family_name = set(f[0].split('-')[0] for f in web_family)
      web_family_version = parse_version_head(web_family_fonts)
    print('Google Fonts Version of %s is v%s' % (
      args.family,
      google_family_version
    ))
    print('Web Version of %s is v%s' % (
      ', '.join(web_family_name),
      web_family_version
    ))

  elif args.local_compare:
    local_family = [TTFont(f) for f in args.local_compare]
    local_family_version = parse_version_head(local_family)
    local_fonts_name = set(basename(f.split('-')[0]) for f in
                           args.local_compare)
    print('Google Fonts Version of %s is v%s' % (
      args.family,
      google_family_version
    ))
    print('Local Version of %s is v%s' % (
      ','.join(local_fonts_name),
      local_family_version
    ))

  else:
    print('Google Fonts Version of %s is v%s' % (
      args.family,
      google_family_version
    ))


if __name__ == '__main__':
  main()
