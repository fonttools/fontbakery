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
#     $ sudo pip install pillow protobuf fontbakery

import argparse
import glob
import os
import sys
import BaseHTTPServer
import SocketServer
import StringIO
import csv

try:
  from PIL import ImageFont
except:
  print "Needs pillow.\n\nsudo pip install pillow"
from PIL import Image
from PIL import ImageDraw

try:
  from fontTools.ttLib import TTFont
except:
  print "Needs fontTools.\n\nsudo pip install fonttools"

try:
  from google.protobuf import text_format
except:
  print "Needs protobuf.\n\nsudo pip install protobuf"

try:
  from bakery_cli.fonts_public_pb2 import FontProto, FamilyProto
except:
  print "Needs fontbakery.\n\nsudo pip install fontbakery"


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

def get_FamilyProto_Message(path):
    message = FamilyProto()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, message)
    return message

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
        color: lightgrey;
        font-size:10px;
      }
      img {
        margin-left:1em;
      }
      thead {
        background: grey;
      }
      td {
        border-left: 1px lightgrey solid;
        white-space: nowrap;
      }
      tr.old {
        background: lightgrey;
      }
      tr.new {
        background: white;
      }
    </style>
  </head>
  <body>
      <table id="myTable" class="tablesorter">
        <thead>
          <tr>
              <td class="Filename">Filename</td>
              <td class="GFN">GFN</td>
              <td class="Weight">Weight</td>
              <td class="Weight-Int">Weight Int</td>
              <td class="Width">Width</td>
              <td class="Width-Int">Width Int</td>
              <td class="Angle">Angle</td>
              <td class="Angle-Int">Angle Int</td>
              <td class="Usage">Usage</td>
              <td class="Image-Weight">Image Weight</td>
<!--              <td class="Image-Width">Image Width</td> -->
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
<tr class="%s">
  <td class="Filename">%s</td>
  <td class="GFN">%s</td>
  <td class="Weight">%s</td>
  <td class="Weight-Int">%s</td>
  <td class="Width">%s</td>
  <td class="Width-Int">%s</td>
  <td class="Angle">%s</td>
  <td class="Angle-Int">%s</td>
  <td class="Usage">%s</td>
  <td class="Image-Weight">%s</td>
<!--  <td class="Image-Width"></td> -->
</tr>
"""

# Normalizes a set of values from 0 to target_max
def normalize_values(properties, target_max=1.0):
  max_value = 0.0
  for i in range(len(properties)):
    val = float(properties[i]['value'])
    max_value = max(max_value, val)
  for i in range(len(properties)):
    properties[i]['value'] *= (target_max/max_value)

# Maps a list into the integer range from target_min to target_max
# Pass a list of floats, returns the list as ints
# The 2 lists are zippable
def map_to_int_range(weights, target_min=1, target_max=10):
  weights_as_int = []
  weights_ordered = sorted(weights)
  min_value = float(weights_ordered[0])
  max_value = float(weights_ordered[-1])
  target_range = (target_max - target_min)
  float_range = (max_value - min_value)
  for weight in weights:
    weight = target_min + int(target_range * ((weight - min_value) / float_range))
    weights_as_int.append(weight)
  return weights_as_int


def main():
  description = """Calculates the visual weight, width or italic angle of fonts.

  For width, it just measures the width of how a particular piece of text renders.

  For weight, it measures the darness of a piece of text.

  For italic angle it defaults to the italicAngle property of the font.
  
  Then it starts a HTTP server and shows you the results, or 
  if you pass --debug then it just prints the values.

  Example (all Google Fonts files, all existing data):
    compute_font_metrics.py --files="fonts/*/*/*.ttf" --existing=fonts/tools/font-metadata.csv
  """
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument("-f", "--files", default="*", 
    help="The pattern to match for finding ttfs, eg 'folder_with_fonts/*.ttf'.")
  parser.add_argument("-d", "--debug", default=False, action='store_true',
    help="Debug mode, just print results")
  parser.add_argument("-e", "--existing", default=False, 
    help="Path to existing font-metadata.csv")
  args = parser.parse_args()

  # show help if no args
  if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit()

  # analyse fonts
  fontinfo = {}
  fontinfo = analyse_fonts(glob.glob(args.files), fontinfo)

  # normalise weights
  weights = []
  for fontfile in sorted(fontinfo.keys()):
    weights.append(fontinfo[fontfile]["weight"])
  ints = map_to_int_range(weights)
  for count, fontfile in enumerate(sorted(fontinfo.keys())):
    fontinfo[fontfile]['weight_int'] = ints[count]

  # normalise widths
  widths = []
  for fontfile in sorted(fontinfo.keys()):
    widths.append(fontinfo[fontfile]["width"])
  ints = map_to_int_range(widths)
  for count, fontfile in enumerate(sorted(fontinfo.keys())):
    fontinfo[fontfile]['width_int'] = ints[count]

  # normalise angles
  angles = []
  for fontfile in sorted(fontinfo.keys()):
    angle = abs(fontinfo[fontfile]["angle"])
    angles.append(angle)
  ints = map_to_int_range(angles)
  for count, fontfile in enumerate(sorted(fontinfo.keys())):
    fontinfo[fontfile]['angle_int'] = ints[count]
  
  # include existing values
  if args.existing:
    with open(args.existing, 'rb') as csvfile:
        existing_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(existing_data) # skip first row as its not data
        for row in existing_data:
          gfn = row[0]
          fontfile = "existing " + gfn
          fontinfo[fontfile] = {"weight": "None", 
                                "weight_int": row[1],
                                "width": "None", 
                                "width_int": row[3],
                                "angle": "None", 
                                "angle_int": row[2],
                                "img_weight": None,
                                "img_width": None,
                                "usage": row[4],
                                "gfn": gfn
                               }

  # if we are debugging, just print the stuff
  if args.debug:
    items = ["weight", "weight_int", "width", "width_int", 
             "angle", "angle_int", "usage", "gfn"]
    for fontfile in sorted(fontinfo.keys()):
       print fontfile, 
       for item in items:
         print fontinfo[fontfile][item],
       print ""
    sys.exit()

  # create a string for the web server
  template_contents = ""
  for fontfile in fontinfo:
    img_weight_html, img_width_html = "", ""
    if fontinfo[fontfile]["img_weight"] is not None:
      img_weight_html = "<img height='50%%' src='data:image/png;base64,%s' />" % (fontinfo[fontfile]["img_weight"])
      #img_width_html  = "<img height='50%%' src='data:image/png;base64,%s' />" % (fontinfo[fontfile]["img_width"])
    old_or_new = "new"
    if fontfile.startswith("existing"):
      old_or_new = "old"
    template_contents += ENTRY_TEMPLATE % (old_or_new,
                                           fontfile, 
                                           fontinfo[fontfile]["gfn"],
                                           fontinfo[fontfile]["weight"],
                                           fontinfo[fontfile]["weight_int"],
                                           fontinfo[fontfile]["width"],
                                           fontinfo[fontfile]["width_int"],
                                           fontinfo[fontfile]["angle"],
                                           fontinfo[fontfile]["angle_int"],
                                           fontinfo[fontfile]["usage"],
                                           img_weight_html)
                                           #img_width_html)

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
      if s.path.endswith(".js"):
        if os.path.exists(s.path):
          s.wfile.write(open(s.path).read())
          s.send_response(200)
        else:
          s.wfile.write("404 Not found: '{}'".format(s.path))
          s.send_response(404)
      else:
        s.wfile.write(debug_page_html)
        s.send_response(200)
        s.send_header("Content-type", "text/html")
      s.end_headers()


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

def get_gfn(fontfile):
  gfn = "unknown"
  metadata = os.path.join(os.path.dirname(fontfile), "METADATA.pb")
  if os.path.exists(metadata):
    family = get_FamilyProto_Message(metadata)
    for font in family.fonts:
      if font.filename in fontfile:
        gfn = "{}:{}:{}".format(family.name, font.style, font.weight)
        break

  return gfn

# Returns fontinfo dict
def analyse_fonts(files, fontinfo):
  # run the analysis for each file, in sorted order
  for fontfile in sorted(files):
    # if blacklisted the skip it
    if is_blacklisted(fontfile):
      print >> sys.stderr, "%s is blacklisted." % fontfile
      continue
    # put metadata in dictionary
    darkness, img_d = get_darkness(fontfile)
    width, img_w = get_width(fontfile)
    angle = get_angle(fontfile)
    gfn = get_gfn(fontfile)
    fontinfo[fontfile] = {"weight": darkness,
                          "width": width,
                          "angle": angle,
                          "img_weight": img_d, 
                          "img_width": img_w, 
                          "usage": "unknown", 
                          "gfn": gfn
                         }
  return fontinfo


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
