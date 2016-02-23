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
    <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.0.0-beta1/jquery.min.js"></script> 
    <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.25.4/js/jquery.tablesorter.min.js"></script> 
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
      <table id="myTable" class="tablesorter">
        <thead>
          <tr>
              <td>Filename</td>
              <td>Weight</td>
              <td>Width</td>
              <td>Angle</td>
              <td>Image Weight</td>
              <td>Image Width</td>
          </tr>
        </thead>
        %s
      </table>
    <script type="text/javascript">
      $(document).ready(function() 
          { 
              $("#myTable").tablesorter(); 
          } 
      ); 
    </script>
  </body>
</html>
"""

# When outputing the debug HTML, this is used to show a single font.
ENTRY_TEMPLATE = """
<tr>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td><img width='50%%' src='data:image/png;base64,%s' /></td>
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
  For italic angle it defaults to the italicAngle property of the font.
  
  Then it starts a HTTP server and shows you the results
  """
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument("-f", "--files", default="*", help="The pattern to match for finding ttfs, eg 'folder_with_fonts/*.ttf'.")
  parser.add_argument("-d", "--debug", default=False, help="Debug mode, just print results")
  args = parser.parse_args()

  # show help if no args
  if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit()

  # dictionary to be keyed by filename
  fontinfo = {}

  # create a string for the web server
  template_contents = ""

  # run the analysis for each file, in sorted order
  fontfiles = glob.glob(args.files)
  for fontfile in sorted(fontfiles):
    # if blacklisted the skip it
    if is_blacklisted(fontfile):
      print >> sys.stderr, "%s is blacklisted." % fontfile
      continue
    # put metadata in dictionary
    d, img_d = get_darkness(fontfile)
    w, img_w = get_width(fontfile)
    a = get_angle(fontfile)
    fontinfo[fontfile] = {"weight": d, "width": w, "angle": a, "img_weight": img_d, "img_width": img_w}
    template_contents += ENTRY_TEMPLATE % (fontfile, d, w, a, img_d, img_w)

  debug_page_html = DEBUG_TEMPLATE % template_contents

  # The port on which the debug server will be hosted.
  PORT = 8080

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

  httpd = None
  while httpd is None:
    try:
      httpd = SocketServer.TCPServer(("", PORT), DebugHTTPHandler)
    except:
      print PORT, "is in use, trying", PORT + 1
      PORT = PORT + 1

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
  ttfont.close()
  return angle

# Returns the width, given a filename of a ttf.
# This is in pixels so should be normalized.
def get_width(fontfile):
  # Render the test text using the font onto an image.
  font = ImageFont.truetype(fontfile, FONT_SIZE)
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
  return text_width, get_base64_image(img)


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
    raise
    darkness = 0.0

  # NOOP this because it reduces darkness to 0.0 always
  # Weight the darkness by x-height.
  # x_height = get_x_height(fontfile)
  #darkness *= (x_height / FONT_SIZE)

  return darkness, get_base64_image(img)

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
