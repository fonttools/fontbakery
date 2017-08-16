#!/usr/bin/env python
"""
Generate a test html snippet for a family hosted on fonts.google.com

This script works well for quickly producing test cases using jsbin.

$ fontbakery family-html-snippet "Exo" "Hello World"
>>> ...
<html>
  <head>
    <link href="https://fonts.googleapis.com/css?family=Exo"/rel="stylesheet">
    <style>
      .g{font-family: 'Exo'; font-weight:400;}
      .h{font-family: 'Exo'; font-weight:400; font-style: italic;}
      .m{font-family: 'Exo'; font-weight:700;}
      .n{font-family: 'Exo'; font-weight:700; font-style: italic;}
    </style>
  </head>
  <body>
    <p class='g'>Hello World</p>
    <p class='h'>Hello World</p>
    <p class='m'>Hello World</p>
    <p class='n'>Hello World</p>
  </body>
</html>
"""
import json
import requests
import sys
from argparse import ArgumentParser

GF_API = "https://www.googleapis.com/webfonts/v1/webfonts?key={}"

GF_API_WEIGHT_TO_CSS_WEIGHT = {
  "100": "100",
  "100italic": "100i",
  "200": "200",
  "200italic": "200i",
  "300": "300",
  "300italic": "300i",
  "regular": "400",
  "italic": "400i",
  "500": "500",
  "500italic": "500i",
  "600": "600",
  "600italic": "600i",
  "700": "700",
  "700italic": "700i",
  "800": "800",
  "800italic": "800i",
  "900": "900",
  "900italic": "900i"
}

API_TO_CSS_STYLE_NAME = {
  "100": "a",
  "100i": "b",
  "200": "c",
  "200i": "d",
  "300": "e",
  "300i": "f",
  "400": "g",
  "400i": "h",
  "500": "i",
  "500i": "j",
  "600": "k",
  "600i": "l",
  "700": "m",
  "700i": "n",
  "800": "o",
  "800i": "p",
  "900": "q",
  "900i": "r",
}


def get_gf_family(family, api_key):
  """Get data of the given family hosted on Google Fonts"""
  request = requests.get(GF_API.format(api_key))

  try:
    response = json.loads(request.text)
    if "error" in response:
      if response["error"]["errors"][0]["reason"] == "keyInvalid":
        sys.exit(("The Google Fonts API key '{}'"
                  " was rejected as being invalid !").format(api_key))
      else:
        sys.exit(("There were errors in the"
                  " Google Fonts API request:"
                  " {}").format(response["error"]))
    else:
      gf_families = response
  except (ValueError, KeyError):
    sys.exit("Unable to load and parse data from Google Web Fonts API.")

  for item in gf_families['items']:
    if family == item['family']:
        return item
  return False


def get_family_styles(gf_family):
  """Get all the styles of a family"""
  styles = []
  if gf_family:
      for var in gf_family['variants']:
        styles.append((GF_API_WEIGHT_TO_CSS_WEIGHT[var]))
  return styles


def get_family_subsets(family_subsets, gf_family):
  """Get all the valid subsets from the given family"""
  valid_subsets = []
  if family_subsets:
    for subset in family_subsets:
      if subset in gf_family['subsets']:
        valid_subsets.append(subset)
  return valid_subsets


def gen_head_webfonts(family, styles, subsets=None):
  """Gen the html snippet to load fonts"""
  server = '"https://fonts.googleapis.com/css?family='
  if subsets:
    return '<link href=%s%s:%s&amp;subset=%s" /rel="stylesheet">' % (
      server, family.replace(' ', '+'), ','.join(styles), ','.join(subsets)
    )
  return '<link href=%s%s:%s" /rel="stylesheet">' % (
    server, family.replace(' ', '+'), ','.join(styles)
  )


def gen_css_styles(family, styles):
  css = []
  for style in styles:
    if style.endswith('i'):
      css.append((".%s{font-family: '%s'; "
                  "font-weight:%s; "
                  "font-style: italic;}" % (
                    API_TO_CSS_STYLE_NAME[style],
                    family,
                    style[:-1])
                  ))
    else:
      css.append((".%s{font-family: '%s'; "
                  "font-weight:%s;}" % (
                    API_TO_CSS_STYLE_NAME[style],
                    family,
                    style)
                  ))
  return css


def gen_body_text(styles, sample_text):
  html = []
  for style in styles:
    html.append("<p class='%s'>%s</p>" % (
      API_TO_CSS_STYLE_NAME[style],
      sample_text)
    )
  return html


def main():
  parser = ArgumentParser(description=__doc__)
  parser.add_argument('key',
                      help='Key from Google Fonts Developer API')
  parser.add_argument('family',
                      help='family name on fonts.google.com')
  parser.add_argument('sample_text',
                      help='sample text used for each font')
  parser.add_argument('--subsets', nargs='+',
                      help='family subset(s) seperated by a space')
  args = parser.parse_args()

  gf_family = get_gf_family(args.family, args.key)
  family_styles = get_family_styles(gf_family)
  family_subsets = get_family_subsets(args.subsets, gf_family)

  if family_subsets:
    head_fonts = gen_head_webfonts(args.family, family_styles, family_subsets)
  else:
    head_fonts = gen_head_webfonts(args.family, family_styles)

  css_styles = gen_css_styles(args.family, family_styles)
  body_text = gen_body_text(family_styles, args.sample_text)

  html = """
<html>
  <head>
    %s
    <style>
      %s
    </style>
  </head>
  <body>
    %s
  </body>
</html>""" % (
    head_fonts,
    '\n      '.join(css_styles),
    '\n    '.join(body_text)
  )
  print html


if __name__ == '__main__':
  main()
