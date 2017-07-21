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
from argparse import ArgumentParser

GF_API = 'http://tinyurl.com/m8o9k39'

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


def get_family_styles(family):
  """Get all the styles of a family hosted on Google Fonts"""
  styles = []
  request = requests.get(GF_API)
  gf_families = json.loads(request.text)
  for item in gf_families['items']:
    if family == item['family']:
      for var in item['variants']:
        styles.append((GF_API_WEIGHT_TO_CSS_WEIGHT[var]))
  return styles


def gen_head_webfonts(family, styles):
  """Gen the html snippet to load fonts"""
  server = '"https://fonts.googleapis.com/css?family='
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
  parser.add_argument('family',
                      help='family name on fonts.google.com')
  parser.add_argument('sample_text',
                      help='sample text used for each font')
  args = parser.parse_args()

  family_styles = get_family_styles(args.family)

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
