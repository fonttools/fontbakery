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

def _unpack(stream):
  # L = unsignedlong 4 bytes
  while True:
    head = stream.read(8)
    if not head:
      break
    jsonlen, fontlen = struct.unpack('II', head)
    desc = json.loads(stream.read(jsonlen).decode('utf-8'))
    font = TTFont(BytesIO(stream.read(fontlen)))
    yield (desc, font)

def build_check_results_table(report_file):
  return "FOO"

@app.route('/runchecks', methods=['POST'])
def run_fontbakery():

  config = {
    'verbose': False,
    'ghm': False,
    'json': True,
    'error': True,
    'autofix': False,
    'inmem': True,
    'files': _unpack(request.stream)
  }

  reports = check_ttf(config)

  report_data = ""
  i = 1
  tabs = ""
  for desc, report_file in reports:
    if desc["filename"] is not None:
      tabs += ('<li><a href="#tabs-{}">'
               '{}</a></li>').format(i, desc["filename"])
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
