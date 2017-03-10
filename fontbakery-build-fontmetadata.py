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
# python tools/fontbakery-build-fontmetadata.py -h
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
import collections
import re
from fonts_public_pb2 import FontProto, FamilyProto

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
  from flask import Flask, jsonify, request
except:
  sys.exit("Needs flask.\n\nsudo pip install flask")

# The font size used to test for weight and width.
FONT_SIZE = 30

# The text used to test weight and width. Note that this could be
# problematic if a given font doesn't have latin support.
TEXT = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvXxYyZz"

# Fonts that cause problems: any filenames containing these letters
# will be skipped.
# TODO: Investigate why these don't work.
BLACKLIST = [
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
  "Benne",
  "Kolar",
  "KumarOne",
  "Mogra",
  "Redacted",  # Its pure black so it throws everything off
  "AdobeBlank", # Testing font, gives ZeroDivisionError: float division by zero
]

# nameID definitions for the name table:
NAMEID_COPYRIGHT_NOTICE = 0
NAMEID_FONT_FAMILY_NAME = 1
NAMEID_FONT_SUBFAMILY_NAME = 2
NAMEID_UNIQUE_FONT_IDENTIFIER = 3
NAMEID_FULL_FONT_NAME = 4
NAMEID_VERSION_STRING = 5
NAMEID_POSTSCRIPT_NAME = 6
NAMEID_TRADEMARK = 7
NAMEID_MANUFACTURER_NAME = 8
NAMEID_DESIGNER = 9
NAMEID_DESCRIPTION = 10
NAMEID_VENDOR_URL = 11
NAMEID_DESIGNER_URL = 12
NAMEID_LICENSE_DESCRIPTION = 13
NAMEID_LICENSE_INFO_URL = 14
# Name ID 15 is RESERVED
NAMEID_TYPOGRAPHIC_FAMILY_NAME = 16
NAMEID_TYPOGRAPHIC_SUBFAMILY_NAME = 17
NAMEID_COMPATIBLE_FULL_MACONLY = 18
NAMEID_SAMPLE_TEXT = 19
NAMEID_POSTSCRIPT_CID_NAME = 20
NAMEID_WWS_FAMILY_NAME = 21
NAMEID_WWS_SUBFAMILY_NAME = 22
NAMEID_LIGHT_BACKGROUND_PALETTE = 23
NAMEID_DARK_BACKGROUD_PALETTE = 24

def generate_italic_angle_images():
  from PIL import Image, ImageDraw
  import math
  for i in range(10):
    angle = 30*(float(i)/10) * 3.1415/180
    width = 2000
    height = 500
    lines = 250
    im = Image.new('RGBA', (width,height), (255,255,255,0))
    spacing = width/lines
    draw = ImageDraw.Draw(im)
    for j in range(lines):
      draw.line([j*spacing - 400, im.size[1], j*spacing - 400 + im.size[1]*math.tan(angle), 0], fill=(50,50,255,255))
    del draw

    imagesdir = os.path.join(os.path.dirname(__file__), "fontmetadata_tool", "images")
    if not os.path.isdir(imagesdir):
      os.mkdir(imagesdir)
    filepath = os.path.join(imagesdir, "angle_{}.png".format(i+1))
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
<img height='30%%' src='data:image/png;base64,%s'
     style="background:url(fontmetadata_tool/images/angle_%d.png) 0 0 no-repeat;" />
"""


description = """Calculates the visual weight, width or italic angle of fonts.

  For width, it just measures the width of how a particular piece of text renders.

  For weight, it measures the darkness of a piece of text.

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
parser.add_argument("-m", "--missingmetadata", default=False, action='store_true',
                    help="Only process fonts for which metadata is not available yet")
parser.add_argument("-o", "--output", default="output.csv", required=True, 
                    help="CSV data output filename")


def main():
  args = parser.parse_args()

  # show help if no args
  if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit()

  files_to_process = []
  for arg_files in args.files:
    files_to_process.extend(glob.glob(arg_files))

  if len(files_to_process) == 0:
    print("No font files were found!")
    sys.exit()

  if args.missingmetadata:
    if args.existing == False:
      sys.exit("you must use the --existing attribute in conjunction with --missingmetadata")
    else:
      rejected = []
      with open(args.existing, 'rb') as csvfile:
        existing_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(existing_data) # skip first row as its not data
        for row in existing_data:
          name = row[0].split(':')[0]
          if ' ' in name:
            name = ''.join(name.split(' '))
          for f, fname in enumerate(files_to_process):
            if name in fname:
              files_to_process.pop(f)
              rejected.append(fname + ":" + row[0])

      print("These files were removed from the list:\n" + '\n'.join(rejected))

  # analyse fonts
  fontinfo = analyse_fonts(files_to_process)

  if fontinfo == {}:
    print("All specified fonts are blacklisted!")
    sys.exit()

  # normalise weights
  weights = []
  for key in sorted(fontinfo.keys()):
    weights.append(fontinfo[key]["weight"])
  ints = map_to_int_range(weights)
  for count, key in enumerate(sorted(fontinfo.keys())):
    fontinfo[key]['weight_int'] = ints[count]

  # normalise widths
  widths = []
  for key in sorted(fontinfo.keys()):
    widths.append(fontinfo[key]["width"])
  ints = map_to_int_range(widths)
  for count, key in enumerate(sorted(fontinfo.keys())):
    fontinfo[key]['width_int'] = ints[count]

  # normalise angles
  angles = []
  for fontfile in sorted(fontinfo.keys()):
    angle = abs(fontinfo[fontfile]["angle"])
    angles.append(angle)
  ints = map_to_int_range(angles)
  for count, key in enumerate(sorted(fontinfo.keys())):
    fontinfo[key]['angle_int'] = ints[count]
  
  # include existing values
  if args.existing and args.missingmetadata == False:
    with open(args.existing, 'rb') as csvfile:
        existing_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(existing_data) # skip first row as its not data
        for row in existing_data:
          gfn = row[0]
          fontinfo[gfn] = {"weight": "None",
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
    for key in sorted(fontinfo.keys()):
       print fontinfo[key]["fontfile"], 
       for item in items:
         print fontinfo[key][item],
       print ""
    sys.exit()

  # generate data for the web server
  # double(<unit>, <precision>, <decimal_point>, <thousands_separator>, <show_unit_before_number>, <nansymbol>)
  grid_data = {
    "metadata": [
      {"name":"fontfile","label":"filename","datatype":"string","editable":True},
      {"name":"gfn","label":"GFN","datatype":"string","editable":True},
      {"name":"weight","label":"weight","datatype":"double(, 2, dot, comma, 0, n/a)","editable":True},
      {"name":"weight_int","label":"WEIGHT_INT","datatype":"integer","editable":True},
      {"name":"width","label":"width","datatype":"double(, 2, dot, comma, 0, n/a)","editable":True},
      {"name":"width_int","label":"WIDTH_INT","datatype":"integer","editable":True},
      {"name":"usage","label":"USAGE","datatype":"string","editable":True,
        "values": {"header":"header", "body":"body", "unknown":"unknown"}
      },
      {"name":"angle","label":"angle","datatype":"double(, 2, dot, comma, 0, n/a)","editable":True}, 
      {"name":"angle_int","label":"ANGLE_INT","datatype":"integer","editable":True},
      {"name":"image","label":"image","datatype":"html","editable":False},
    ],
    "data": []
  }

  #renders a sample of a few glyphs and
  #returns a PNG image as base64 data
  def render_slant_chars(fontfile):
    SAMPLE_CHARS = "HNHNUHNHN"
    font = ImageFont.truetype(fontfile, FONT_SIZE * 10)
    try:
      text_width, text_height = font.getsize(SAMPLE_CHARS)
    except:
      text_width, text_height = 1, 1
    img = Image.new('RGBA', (text_width, 20+text_height))
    draw = ImageDraw.Draw(img)
    try:
      draw.text((0, 0), SAMPLE_CHARS, font=font, fill=(0, 0, 0))
    except:
      pass
    return get_base64_image(img)

  field_id = 1
  for key in fontinfo:
    values = fontinfo[key]
    if values["gfn"] == "unknown":
      continue
    img_weight_html, img_width_html = "", ""
    if values["img_weight"] is not None:
      img_weight_html = "<img height='50%%' src='data:image/png;base64,%s' />" % (values["img_weight"])
      #img_width_html  = "<img height='50%%' src='data:image/png;base64,%s' />" % (values["img_width"])

    img_angle_html = ""
    if ".ttf" in values["fontfile"]:
      img_angle_html = ITALIC_ANGLE_TEMPLATE % (render_slant_chars(values["fontfile"]), values["angle_int"])

    values["image"] = img_weight_html
    values["angle_image"] = img_angle_html
    grid_data["data"].append({"id": field_id, "values": values})
    field_id += 1

  def save_csv():
    filename = args.output
    #count = 0
    #while os.isfile(filename):
    #  print filename, "exists, trying", filename + count
    #  filename = filename + count
    with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"')
        writer.writerow(["GFN","FWE","FIA","FWI","USAGE"]) # first row has the headers
        for data in grid_data["data"]:
          values = data["values"]
          gfn = values['gfn']
          fwe = values['weight_int']
          fia = values['angle_int']
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

  print "Access http://127.0.0.1:5000/fontmetadata_tool/index.html\n"
  app.run()

#====================================================================
# Here we copy/paste and adapt a bunch of code
# from https://github.com/google/fonts/blob/master/tools/add_font.py
# following the policy of keeping this script standalone.
#====================================================================

class Error(Exception):
  """Base for Google Fonts errors."""

class ParseError(Error):
  """Exception used when parse failed."""

_FAMILY_WEIGHT_REGEX = r'([^/-]+)-(\w+)\.ttf$'

# The canonical [to Google Fonts] name comes before any aliases
_KNOWN_WEIGHTS = collections.OrderedDict([
    ('Thin', 100),
    ('Hairline', 100),
    ('ExtraLight', 200),
    ('Light', 300),
    ('Regular', 400),
    ('', 400),  # Family-Italic resolves to this
    ('Medium', 500),
    ('SemiBold', 600),
    ('Bold', 700),
    ('ExtraBold', 800),
    ('Black', 900)
])

FileFamilyStyleWeightTuple = collections.namedtuple(
    'FileFamilyStyleWeightTuple', ['file', 'family', 'style', 'weight'])

def StyleWeight(styleweight):
  """Breaks apart a style/weight specifier into a 2-tuple of (style, weight).

  Args:
    styleweight: style/weight string, e.g. Bold, Regular, or ExtraLightItalic.
  Returns:
    2-tuple of style (normal or italic) and weight.
  """
  if styleweight.endswith('Italic'):
    return ('italic', _KNOWN_WEIGHTS[styleweight[:-6]])

  return ('normal', _KNOWN_WEIGHTS[styleweight])

def FamilyName(fontname):
  """Attempts to build family name from font name.

  For example, HPSimplifiedSans => HP Simplified Sans.

  Args:
    fontname: The name of a font.
  Returns:
    The name of the family that should be in this font.
  """
  # SomethingUpper => Something Upper
  fontname = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', fontname)
  # Font3 => Font 3
  fontname = re.sub('([a-z])([0-9]+)', r'\1 \2', fontname)
  # lookHere => look Here
  return re.sub('([a-z0-9])([A-Z])', r'\1 \2', fontname)

def FileFamilyStyleWeight(filename):
  """Extracts family, style, and weight from Google Fonts standard filename.

  Args:
    filename: Font filename, eg Lobster-Regular.ttf.
  Returns:
    FileFamilyStyleWeightTuple for file.
  Raises:
    ParseError: if file can't be parsed.
  """
  m = re.search(_FAMILY_WEIGHT_REGEX, filename)
  if not m:
    raise ParseError('Could not parse %s' % filename)
  sw = StyleWeight(m.group(2))
  return FileFamilyStyleWeightTuple(filename, FamilyName(m.group(1)), sw[0],
                                    sw[1])

def _FileFamilyStyleWeights(fontdir):
  """Extracts file, family, style, weight 4-tuples for each font in dir.

  Args:
    fontdir: Directory that supposedly contains font files for a family.
  Returns:
    List of FileFamilyStyleWeightTuple ordered by weight, style
    (normal first).
  Raises:
    OSError: If the font directory doesn't exist (errno.ENOTDIR) or has no font
    files (errno.ENOENT) in it.
    RuntimeError: If the font directory appears to contain files from multiple
    families.
  """
  if not os.path.isdir(fontdir):
    raise OSError(errno.ENOTDIR, 'No such directory', fontdir)

  files = glob.glob(os.path.join(fontdir, '*.ttf'))
  if not files:
    raise OSError(errno.ENOENT, 'no font files found')

  result = [FileFamilyStyleWeight(f) for f in files]
  def _Cmp(r1, r2):
    return cmp(r1.weight, r2.weight) or -cmp(r1.style, r2.style)
  result = sorted(result, _Cmp)

  family_names = {i.family for i in result}
  if len(family_names) > 1:
    raise RuntimeError('Ambiguous family name; possibilities: %s'
                       % family_names)

  return result

def get_gfn(fontfile):
  gfn = "unknown"
  fontdir = os.path.dirname(fontfile)
  metadata = os.path.join(fontdir, "METADATA.pb")
  if os.path.exists(metadata):
    family = get_FamilyProto_Message(metadata)
    for font in family.fonts:
      if font.filename in fontfile:
        gfn = "{}:{}:{}".format(family.name, font.style, font.weight)
        break
  else:
    try:
      attributes = _FileFamilyStyleWeights(fontdir)
      for (fontfname, family, style, weight) in attributes:
        if fontfname in fontfile:
          gfn = "{}:{}:{}".format(family, style, weight)
          break
    except:
      pass

  if gfn == 'unknown':
    #This font lacks a METADATA.pb file and also failed
    # to auto-detect the GFN value. As a last resort
    # we'll try to extract the info from the NAME table entries.
    try:
      ttfont = TTFont(fontfile)
      for entry in ttfont['name'].names:
        if entry.nameID == NAMEID_FONT_FAMILY_NAME:
          family = entry.string.decode(entry.getEncoding()).encode('ascii', 'ignore').strip()
        if entry.nameID == NAMEID_FONT_SUBFAMILY_NAME:
          style, weight = StyleWeight(entry.string.decode(entry.getEncoding()).encode('ascii', 'ignore').strip())
      ttfont.close()
      if family != "": #avoid empty string in cases of misbehaved family names in the name table
        gfn = "{}:{}:{}".format(family, style, weight)
        print ("Detected GFN from name table entries: '{}' (file='{}')".format(gfn, fontfile))
    except:
      #This seems to be a really bad font file...
      pass

  if gfn == 'unknown':
    print ("Failed to detect GFN value for '{}'. Defaults to 'unknown'.".format(fontfile))

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
    fontinfo[gfn] = {"weight": darkness,
                     "width": width,
                     "angle": angle,
                     "img_weight": img_d,
                     "img_width": img_w,
                     "usage": "unknown",
                     "gfn": gfn,
                     "fontfile": fontfile
                    }
  return fontinfo


# Returns whether a font is on the blacklist.
def is_blacklisted(filename):
  # first check for explicit blacklisting:
  for name in BLACKLIST:
    if name in filename:
      return True

  # otherwise, blacklist fonts with a bad set of hinting tables:
  ttfont = TTFont(filename)
  hinting_tables = ["fpgm", "prep", "cvt"]

  found = []
  for table in hinting_tables:
    if table in ttfont:
      found.append(table)

  no_hinting_table_found = (found == [])
  all_hinting_tables_found = (found == hinting_tables)

  # we're looking for all or nothing here:
  good_font = all_hinting_tables_found or no_hinting_table_found
  if not good_font:
    print >> sys.stderr, "Found the following instruction tables: %s" % found
    print >> sys.stderr, "Expected %s or no table at all." % hinting_tables
    return True
  else:
    return False  # not blacklisted


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
