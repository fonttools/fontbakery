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

@app.route('/runchecks', methods=['POST'])
def run_fontbakery():
  hotfixing = False  # TODO: let the user choose.

  if hotfixing:
    result = BytesIO()
    zipf = zipfile.ZipFile(result,  "w")

  config = {
    'verbose': False,
    'ghm': True,
    'json': False,
    'error': True,
    'autofix': False,
    'inmem': True,
    'files': _unpack(request.stream)
  }

  reports = check_ttf(config)

# TODO:
#    if hotfixing:
#      # write the font file to the zip
#      fontIO = BytesIO()
#      font.save(fontIO)
#      fontData = fontIO.getvalue()
#      zipf.writestr(filename, fontData)

  if hotfixing:
    zipf.close()
    data = result.getvalue()
    response = app.make_response(data)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=fonts-with-changed-names.zip'
    return response
  else:
    from markdown import markdown
    report_data = ""
    for desc, report_file in reports:
      if desc["filename"] is not None:
        report_data += "<h3>{}</h3>{}".format(desc["filename"], markdown(report_file))

    return "<h2>Fontbakery check results</h2><div>{}</div>".format(report_data)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
