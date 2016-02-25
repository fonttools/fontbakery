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
import StringIO
import csv

try:
  from PIL import ImageFont
except:
  sys.exit("Needs pillow.\n\nsudo pip install pillow")
from PIL import Image
from PIL import ImageDraw

try:
  from fontTools.ttLib import TTFont
except:
  sys.exit("Needs fontTools.\n\nsudo pip install fonttools")

try:
  from google.protobuf import text_format
except:
  sys.exit("Needs protobuf.\n\nsudo pip install protobuf")

try:
  from bakery_cli.fonts_public_pb2 import FontProto, FamilyProto
except:
  sys.exit("Needs fontbakery.\n\nsudo pip install fontbakery")

try:
  from flask import Flask, jsonify
except:
  sys.exit("Needs flask.\n\nsudo pip install flask")

try:
  from flask import Flask, jsonify, request
except:
  print "Needs flask.\n\nsudo pip install flask"

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
  "FiraMono",
  # Its pure black so it throws everything off
  "Redacted"
]


def generate_italic_angle_images():
  from PIL import Image, ImageDraw
  import math
  for i in range(10):
    angle = 30*(float(i)/10) * 3.1415/180
    im = Image.new('RGBA', (200,50), (255,255,255,0))
    N = 15
    spacing = 200/N
    draw = ImageDraw.Draw(im)
    for j in range(N):
      draw.line([j*spacing, im.size[1], j*spacing + im.size[1]*math.tan(angle), 0], fill=(50,50,255,255))
    del draw
    filepath = "static/images/angle_{}.png".format(i+1)
    filepath = os.path.join(os.path.dirname(__file__), filepath)
    im.save(filepath, "PNG")

generate_italic_angle_images()

def get_FamilyProto_Message(path):
    message = FamilyProto()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, message)
    return message

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

ITALIC_ANGLE_TEMPLATE = """
<img height='50%%' src='data:image/png;base64,%s'
     style="background:url(images/angle_%d.png) 0 0 no-repeat;" />
"""

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
  parser.add_argument("-f", "--files", default="*", required=True, 
    help="The pattern to match for finding ttfs, eg 'folder_with_fonts/*.ttf'.")
  parser.add_argument("-d", "--debug", default=False, action='store_true',
    help="Debug mode, just print results")
  parser.add_argument("-e", "--existing", default=False,
    help="Path to existing font-metadata.csv")
  parser.add_argument("-o", "--output", default="output.csv", required=True, 
    help="CSV data output filename")
  args = parser.parse_args()

  # show help if no args
  if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit()

  # analyse fonts
  fontinfo = analyse_fonts(glob.glob(args.files))

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

  # generate data for the web server
  # double(<unit>, <precision>, <decimal_point>, <thousands_separator>, <show_unit_before_number>, <nansymbol>)
  grid_data = {
    "metadata": [
      {"name":"fontfile","label":"FONTFILE","datatype":"string","editable":True},
      {"name":"gfn","label":"GFN","datatype":"string","editable":True},
      {"name":"weight","label":"WEIGHT","datatype":"double(, 2, dot, comma, 0, n/a)","editable":True},
      {"name":"weight_int","label":"WEIGHT_INT","datatype":"integer","editable":True},
      {"name":"width","label":"WIDTH","datatype":"double(, 2, dot, comma, 0, n/a)","editable":True},
      {"name":"width_int","label":"WIDTH_INT","datatype":"integer","editable":True},
      {"name":"angle","label":"ANGLE","datatype":"double(, 2, dot, comma, 0, n/a)","editable":True}, 
      {"name":"angle_image","label":"ANGLE_IMAGE","datatype":"html","editable":False},
      {"name":"angle_int","label":"ANGLE_INT","datatype":"integer","editable":True},
      {"name":"usage","label":"USAGE","datatype":"string","editable":True,
        "values": {"header":"header", "body":"body", "unknown":"unknown"}
      },
      {"name":"image","label":"IMAGE","datatype":"html","editable":False},
    ],
    "data": []
  }

  #renders a sample of a few glyphs and
  #returns a PNG image as base64 data
  def render_HMNU_sample(fontfile):
    SAMPLE_CHARS = "HMNU"
    font = ImageFont.truetype(fontfile, FONT_SIZE)
    try:
      text_width, text_height = font.getsize(SAMPLE_CHARS)
    except:
      text_width, text_height = 1, 1
    img = Image.new('RGBA', (text_width, 2*text_height))
    draw = ImageDraw.Draw(img)
    try:
      draw.text((0, -text_height/3), SAMPLE_CHARS, font=font, fill=(0, 0, 0)) #the y coordinate positioning is a hack. FIXME!
    except:
      pass
    return get_base64_image(img)

  field_id = 1
  for fontfile in fontinfo:
    img_weight_html, img_width_html = "", ""
    if fontinfo[fontfile]["img_weight"] is not None:
      img_weight_html = "<img height='50%%' src='data:image/png;base64,%s' />" % (fontinfo[fontfile]["img_weight"])
      #img_width_html  = "<img height='50%%' src='data:image/png;base64,%s' />" % (fontinfo[fontfile]["img_width"])

    img_angle_html = ""
    if ".ttf" in fontfile:
      img_angle_html = ITALIC_ANGLE_TEMPLATE % (render_HMNU_sample(fontfile), fontinfo[fontfile]["angle_int"])

    values = fontinfo[fontfile]
    values["fontfile"] = fontfile
    values["image"] = img_weight_html
    values["angle_image"] = img_angle_html
    grid_data["data"].append({"id": field_id, "values": values})
    field_id += 1

  def save_csv():
    with open(args.output, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"')
        writer.writerow(["GFN","FWE","FIA","FWI","USAGE"]) # first row has the headers
        for data in grid_data["data"]:
          values = data["values"]
          gfn = values['gfn']
          fwe = values['weight_int']
          fia = values['angle']
          fwi = values['width_int']
          usage = values['usage']
          writer.writerow([gfn, fwe, fia, fwi, usage])
    return 'ok'

  app = Flask(__name__)

  @app.route('/data.json')
  def json_data():
    return jsonify(grid_data)

  @app.route('/update', methods=['POST'])
  def update():
    rowid = request.form['id']
    newvalue = request.form['newvalue']
    colname = request.form['colname']
    for row in grid_data["data"]:
      if row['id'] == int(rowid):
        row['values'][colname] = newvalue
    return save_csv()

  print "Access http://127.0.0.1:5000/static/index.html\n"
  app.run()



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
def analyse_fonts(files):
  fontinfo = {}
  # run the analysis for each file, in sorted order
  for count, fontfile in enumerate(sorted(files)):
    # if blacklisted the skip it
    if is_blacklisted(fontfile):
      print >> sys.stderr, "%s is blacklisted." % fontfile
      continue
    else:
      print("[{}/{}] {}...".format(count+1, len(files), fontfile))
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
  darkness = 0.0
  for i, value in enumerate(alpha):
    avg += (i / 255.0) * value
  try:
    darkness = avg / (text_width * text_height)
  except:
    raise

  # Weight the darkness by x-height for more accurate results
  # FIXME Perhaps this should instead *CROP* the image 
  # to the bbox of the letters, to remove additional 
  # whitespace created by vertical metrics, even for more accuracy
  x_height = get_x_height(fontfile)
  darkness *= (x_height / float(FONT_SIZE))
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
