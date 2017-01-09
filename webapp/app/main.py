# [START app]
from __future__ import print_function
import logging
from flask import Flask, make_response, request, Response
from fontTools.ttLib import TTFont
import struct
from io import BytesIO
import json
import zipfile
app = Flask(__name__)
check_ttf = __import__("fbCheckTTF").fontbakery_check_ttf
target_font = __import__("fbCheckTTF").target_font

# NOTE:
# JSON description format is a dictionary with the following fields:
#  -> filename
#  -> familyName
#  -> weightName
#  -> isItalic
#  -> version
#  -> vendorID

def _unpack(stream):
  # L = unsignedlong 4 bytes
  while True:
    head = stream.read(8)
    if not head:
      break
    jsonlen, fontlen = struct.unpack('II', head)
    target = target_font()
    target.set_description(json.loads(stream.read(jsonlen).decode('utf-8')))
    target.ttfont = TTFont(BytesIO(stream.read(fontlen)))
    yield target

def build_check_results_table(report_file):
  data = report_file.read()
  return "JSON data:<pre>{}</pre>".format(data)


@app.route('/runchecks', methods=['POST'])
def run_fontbakery():

  config = {
    'verbose': False,
    'ghm': False,
    'json': True,
    'error': True,
    'autofix': False,  # Hotfixes are only supported on the command line.
    'inmem': True, #  Filesystem I/O is forbiden on Google App Engine.
    'webapp': True, #  This will disable a few unsupported features on GAE.
    'files': _unpack(request.stream)
  }

  reports = check_ttf(config)
  report_data = ""
  i = 1
  tabs = ""
  for target, report_file in reports:
    if target is not None:
      tabs += ('<li><a href="#tabs-{}">'
               '{}</a></li>').format(i, target)
      table = build_check_results_table(report_file)
      report_data += ('<div id="tabs-{}">'
                      '{}</div>').format(i, table)
      i+=1

  return '<div id="tabs"><ul>{}</ul>{}</div>'.format(tabs, report_data)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
