#!/usr/bin/python
# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Initially authored by Google and contributed by Filip Zembowicz.
# Further improved by Dave Crossland and Felipe Sanches.
#
# OVERVIEW + USAGE
#
# python compute_font_metrics.py -h
#
# DEPENDENCIES
#
# The script depends on the PIL API (Python Imaging Library)
# If you have pip <https://pypi.python.org/pypi/pip> installed, run:
#
#     $ sudo pip install pillow

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

import argparse
import glob
import sys
import BaseHTTPServer
import SocketServer
import StringIO

from fontTools.ttLib import TTFont

# The font size used to test for weight and width.
FONT_SIZE = 30

# The text used to test weight and width. Note that this could be
# problematic if a given font doesn't have latin support.
TEXT = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvXxYyZz"

# The port on which the debug server will be hosted.
PORT = 8080

# Fonts that cause problems: any filenames containing these letters
# will be skipped.
# TODO: Investigate why these don't work.
BLACKLIST = [
  #IOError: invalid reference (issue #705)
  "Corben",
  #SystemError: tile cannot extend outside image (issue #704)
  "Suwannaphum",
  "KarlaTamil",
  "Khmer",
  "KdamThmor",
  "Battambang",
  "AksaraBaliGalang",
  "Phetsarath",
  "Kantumruy",
  "Nokora",
  "Droid",
  #IOError: execution context too long (issue #703)
  "FiraSans",
  "FiraMono"
]

DEBUG_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <style>
      body {
        font-family: sans-serif;
      }
      div.filename, div.darkess {
        width:100px;
        color:gray;
        font-size:10px;
      }
      img {
        margin-left:1em;
      }
      td {
        border-left: 1px grey solid;
      }
    </style>
  </head>
  <body>
      <table>
        <thead>
          <tr>
              <td>Filename</td>
              <td>Weight</td>
              <td>Italic</td>
              <td>Width</td>
              <td>Angle</td>
              <td>Image</td>
          </tr>
        </thead>
        %s
      </table>
  </body>
</html>
"""

# When outputing the debug HTML, this is used to show a single font.
ENTRY_TEMPLATE = """
<tr>
  <td>%s</td>
  <td>%s</td>
  <td>Italic</td>
  <td>Width</td>
  <td>Angle</td>
  <td><img width='50%%' src='data:image/png;base64,%s' /></td>
</tr>
"""

# Normalizes a set of values from 0 - 1.0
def normalize_values(properties):
  max_value = 0.0
  for i in range(len(properties)):
    val = float(properties[i]['value'])
    max_value = max(max_value, val)

  for i in range(len(properties)):
    properties[i]['value'] /= max_value

def main():
  description = """Calculates the visual weight, width or italic angle of fonts.
  For width, it just measures the width of how a particular piece of text renders.
  For weight, it measures the darness of a piece of text.
  For italic angle it defaults to the italicAngle property of the font
   or prompts the user for hand-correction of the value."""
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument("-f", "--files", default="*", help="The pattern to match for finding ttfs, eg 'folder_with_fonts/*.ttf'.")
  parser.add_argument("-l", "--fontlist", default=False, help="A list of paths to fonts, eg 'fonta.ttf fontb.ttf' or '`ls -1 ~/fonts/*/*/*.ttf`'.")
  parser.add_argument("-d", "--debug", default=False, help="Debug mode, spins up a server to validate results visually.")
  parser.add_argument("-m", "--metric", default="weight", help="What property to measure; ('weight', 'width' or 'angle'.)")
  args = parser.parse_args()

  if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit()

  properties = {}
  fontfiles = glob.glob(args.files)
  for fontfile in fontfiles:
    if is_blacklisted(fontfile):
      print >> sys.stderr, "%s is blacklisted." % fontfile
      continue
    try:
      properties['darkness'] = get_darkness(fontfile)
      properties['width'] = get_width(fontfile)
      properties['angle'] = get_angle(fontfile)
    # except:
    #   print >> sys.stderr, "Couldn't calculate darkness of %s." % fontfile


    normalize_values(properties['width'])

  if args.debug:
    start_debug_server(properties)
  else:
    dump_values(properties)





# Dump the values to the terminal.
def dump_values(properties):
  for font in sorted(properties, key=lambda x: x['value']):
    print font['fontfile'] + "," + str(font['value'])


# Brings up a HTTP server to host a page for visual inspection
def start_debug_server(properties):
  template_contents = ""
  for font in sorted(properties, key=lambda x: x['value']):
    metric = font['value']
    filename = font['fontfile']
    base64img = font['base64img']

    if metric == 0.0:
      print >> sys.stderr, "%s has no metric." % filename
      continue
    template_contents += ENTRY_TEMPLATE % (metric, filename, base64img)

  debug_page_html = DEBUG_TEMPLATE % template_contents

  # Handler that responds to all requests with a single file.
  class DebugHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
      s.send_response(200)
      s.send_header("Content-type", "text/html")
      s.end_headers()
    def do_GET(s):
      s.send_response(200)
      s.send_header("Content-type", "text/html")
      s.end_headers()
      s.wfile.write(debug_page_html)

  httpd = SocketServer.TCPServer(("", PORT), DebugHTTPHandler)

  print "Debug page can be seen at http://127.0.0.1:" + str(PORT)
  print "Kill the server with Ctrl+C"
  httpd.serve_forever()


# Returns whether a font is on the blacklist.
def is_blacklisted(filename):
  for name in BLACKLIST:
    if name in filename:
      return True
  return False


# Returns the italic angle, given a filename of a ttf;
def get_angle(fontfile):
  ttfont = TTFont(fontfile)
  angle = ttfont['post'].italicAngle
  print fontfile, angle
  ttfont.close()
  return {'angle': angle, 'fontfile': fontfile, 'base64img': None}

# Returns the width, given a filename of a ttf.
# This is in pixels so should be normalized.
def get_width(fontfile):
  print fontfile
  # Render the test text using the font onto an image.
  font = ImageFont.truetype(fontfile, FONT_SIZE)
  print font
  try:
      text_width, text_height = font.getsize(TEXT)
  except:
      text_width, text_height = 1, 1 
  img = Image.new('RGBA', (text_width, text_height))
  draw = ImageDraw.Draw(img)
  try:
      draw.text((0, 0), TEXT, font=font, fill=(0, 0, 0))
  except: 
      pass
  return {'text_width': text_width, 'fontfile': fontfile, 'base64img': get_base64_image(img)}


# Returns the darkness, given a filename of a ttf.
def get_darkness(fontfile):
  # Render the test text using the font onto an image.
  font = ImageFont.truetype(fontfile, FONT_SIZE)
  text_width, text_height = font.getsize(TEXT)
  img = Image.new('RGBA', (text_width, text_height))
  draw = ImageDraw.Draw(img)
  draw.text((0, 0), TEXT, font=font, fill=(0, 0, 0))

  # Calculate the average darkness.
  histogram = img.histogram()
  alpha = histogram[768:]
  avg = 0.0
  for i, value in enumerate(alpha):
    avg += (i / 255.0) * value
  try:
    darkness = avg / (text_width * text_height)
  except:
    darkness = 0.0

  # Weight the darkness by x-height.
  x_height = get_x_height(fontfile)
  darkness *= (x_height / FONT_SIZE)

  return {'darkness': darkness, 'fontfile': fontfile, 'base64img': get_base64_image(img)}


# Get the base 64 representation of an image, to use for visual testing.
def get_base64_image(img):
  output = StringIO.StringIO()
  img.save(output, "PNG")
  base64img = output.getvalue().encode("base64")
  output.close()
  return base64img

# Returns the height of the lowercase "x" in a font.
def get_x_height(fontfile):
  font = ImageFont.truetype(fontfile, FONT_SIZE)
  _, x_height = font.getsize("x")
  return x_height


if __name__ == "__main__":
  main()
