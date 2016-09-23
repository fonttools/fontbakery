#!/usr/bin/env python
import os
import json

def uniq(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output

summary = {}
check_results_dir = "./check_results"
for font_dir in os.listdir(check_results_dir):
  abspath = os.path.join(check_results_dir, font_dir)
  if not os.path.isdir(abspath):
    continue
  for f in os.listdir(abspath):
    if not f.endswith("fontbakery.json"):
      continue
    abs_file_path = os.path.join(abspath, f)
    font_results = json.loads(open(abs_file_path).read())
    for entry in font_results:
      if entry['result'] == 'ERROR':
        summary.setdefault(entry['description'], []).append(entry['target'])

list_files = True
filter_name_checks = False

if filter_name_checks:
  checks = [k for k in summary.keys() if 'name' in k]
else:
  checks = summary.keys()

for check_name in checks:
  targets = uniq(summary[check_name])
  if list_files:
    print ("## {}".format(check_name))
    print ("{} files with errors:".format(len(targets)))
    print ("* " + "\n* ".join(targets))
    print ("\n")
  else:
    print ("* [{} errors] '{}'".format(str(len(targets)).rjust(4), check_name))




