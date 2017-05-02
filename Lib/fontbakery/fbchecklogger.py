#!/usr/bin/env python2
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function
import json
import logging
import subprocess
import sys

from fontbakery.targetfont import TargetFont
from fontbakery.constants import (
                                 YELLOW_STR,
                                 GREEN_STR,
                                 BLUE_STR,
                                 RED_STR,
                                 WHITE_STR,
                                 CYAN_STR,
                                 NORMAL
                                 )
class FontBakeryCheckLogger():
  progressbar = False

  def __init__(self, config):
    self.config = config
    self.font = None
    self.json_report_files = []
    self.ghm_report_files = []
    self.reset_report()

  def set_font(self, f):
    self.font = f

  def reset_report(self):
    self.fixes = []
    self.all_checks = {}
    self.current_check = None
    self.default_target = None  # All new checks have this target by default
    self.summary = {"Passed": 0,
                    "Hotfixes": 0,
                    "Skipped": 0,
                    "Errors": 0,
                    "Warnings": 0}

  def update_burndown(self, name, total):

    git_commit = None
    date = "today"
    try:
      git_cmd = ["git",
                 "log",  # display the commid id and message
                 "HEAD~1..HEAD"]  # only for the last commit
      cmd_output = subprocess.check_output(git_cmd,
                                           stderr=subprocess.STDOUT)
      git_commit = cmd_output.split('\n')[0].split("commit")[1].strip()
      date = cmd_output.split('\n')[2].split("Date:")[1].strip()
    except OSError:
      print("Warning: git is not installed!")
      pass

    fname = "burndown.json"
    burn = None
    data = None
    try:
      burn = open(fname, "r")
      js = burn.read()
      data = json.loads(js)
      burn.close()

    except IOError:
      data = {name: {"planned-release": None,  # This is optional.
              "entries": []}}

    burn = open(fname, "w")
    if name not in data.keys():
      data[name] = {"planned-release": None,
                    "entries": []}
    data[name]["entries"].append({"date": date,
                                 # "fontbakery-version": None,
                                  "commit": git_commit.strip(),
                                  "summary": self.summary})
    burn.write(json.dumps(data,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': ')))
    burn.close()

  def output_report(self, a_target):
    self.flush()

    total = 0
    for key in self.summary.keys():
      total += self.summary[key]

    try:
      self.update_burndown(a_target.fullpath, total)
    except:
      # the burndown chart code is breaking Travis.
      # I'll review this tomorrow. For now let's keep things safe here.
      pass

    print ("\nCheck results summary for '{}':".format(a_target.fullpath))
    for key in self.summary.keys():
      occurrences = self.summary[key]
      percent = float(100*occurrences)/total
      print ("  {}:"
             "\t{}\t({}%)".format(YELLOW_STR.format(key),
                                  occurrences,
                                  round(percent, 2)))
    print ("  Total: {} checks.\n".format(total))

    if not self.config['verbose']:
      filtered = {}
      for k in self.all_checks.keys():
        check = self.all_checks[k]
        if check["result"] != "OK":
          filtered[k] = check
      self.all_checks = filtered

    if self.config['json']:
      self.output_json_report(a_target)

    if self.config['ghm']:
      self.output_github_markdown_report(a_target)

  def output_json_report(self, a_target):
    for k in self.all_checks.keys():
      check = self.all_checks[k]
      if isinstance(check['target'], TargetFont):
        # This is silly and actually means the handling of
        # TargetFont is broken somewhere else.
        # This really needs to be properly fixed ASAP!
        check['target'] = check['target'].fullpath

    json_data = json.dumps(self.all_checks,
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': '))

    json_output_filename = a_target.fullpath + ".fontbakery.json"
    json_output = open(json_output_filename, 'w')
    json_output.write(json_data)
    self.json_report_files.append(json_output_filename)

  def output_github_markdown_report(self, a_target):

    markdown_data = "# Fontbakery check results\n"
    all_checks = {}
    for k in self.all_checks.keys():
      check = self.all_checks[k]
      target = check["target"]

      if target in all_checks.keys():
        all_checks[target].append(check)
      else:
        all_checks[target] = [check]

    for target in all_checks.keys():
      markdown_data += "## {}\n".format(target)
      checks = all_checks[target]
      for check in checks:
        msgs = '\n* '.join(check['log_messages'])
        markdown_data += ("### {}\n"
                          "* {}\n\n").format(check['description'], msgs)

    output_filename = a_target.fullpath + ".fontbakery.md"
    ghm_output = open(output_filename, 'w')
    ghm_output.write(markdown_data)
    self.ghm_report_files.append(output_filename)

  def update_progressbar(self):
    tick = {
      "OK": GREEN_STR.format('.'),
      "HOTFIX": BLUE_STR.format('H'),
      "ERROR": RED_STR.format('E'),
      "WARNING": YELLOW_STR.format('W'),
      "SKIP": WHITE_STR.format('S'),
      "INFO": CYAN_STR.format('I'),
      "unknown": RED_STR.format('?')
    }
    if self.progressbar is False:
      return
    else:
      print(tick[self.current_check["result"]], end='')
      sys.stdout.flush()

  def flush(self):
    if self.current_check is not None:
      if self.current_check["result"] == "unknown":
        print(("### CRITICAL ERROR!"
               " It seems that the check number \"{}\""
               " failed to produce any output."
               " This is likely a FontBakery bug."
               " Please fill an issue at"
               " https://github.com/googlefonts/fontbakery/issues/new"
               "\n").format(self.current_check["check_number"]))

      self.update_progressbar()
      check_number = self.current_check["check_number"]
      self.all_checks[check_number] = self.current_check
      self.current_check = None

  def set_priority(self, level):
    self.current_check["priority"] = level

  def new_check(self, check_number, desc):
    self.flush()
    logging.debug("Check #{}: {}".format(check_number, desc))
    self.current_check = {"description": desc,
                          "check_number": check_number,
                          "log_messages": [],
                          "result": "unknown",
                          "priority": NORMAL,
                          "target": self.default_target}
    # Here we save the initial (empty) check result entry so that
    # in case a crash may happen, we'll be able to detect
    # it due to the presence of the key "result": "unknown".
    # For more detail, take a look at this issue:
    # https://github.com/googlefonts/fontbakery/issues/1299
    check_number = self.current_check["check_number"]
    self.all_checks[check_number] = self.current_check

  def set_target(self, value):
    '''sets target of the current check.
       This can be a folder, or a specific TTF file
       or a METADATA.pb file'''

    if self.current_check:
      self.current_check["target"] = value

  def skip(self, msg):
    self.summary["Skipped"] += 1
    logging.info("SKIP: " + msg)
    self.current_check["log_messages"].append("SKIP: " + msg)
    self.current_check["result"] = "SKIP"

  def ok(self, msg):
    self.summary["Passed"] += 1
    logging.info("OK: " + msg)
    self.current_check["log_messages"].append(msg)
    if self.current_check["result"] != "ERROR":
      self.current_check["result"] = "OK"

  def info(self, msg):  # This is just a way for us to keep merely
                        # informative messages on the markdown output
    logging.info("INFO: " + msg)
    self.current_check["log_messages"].append("INFO: " + msg)
    if self.current_check["result"] != "ERROR":
      self.current_check["result"] = "INFO"

  def warning(self, msg):
    self.summary["Warnings"] += 1
    logging.warning(msg)
    self.current_check["log_messages"].append("Warning: " + msg)
    if self.current_check["result"] == "unknown":
      self.current_check["result"] = "WARNING"

  def error(self, msg):
    self.summary["Errors"] += 1
    logging.error(msg)
    self.current_check["log_messages"].append("ERROR: " + msg)
    self.current_check["result"] = "ERROR"

  def hotfix(self, msg):
    self.summary["Hotfixes"] += 1
    logging.info('HOTFIXED: ' + msg)
    self.current_check['log_messages'].append('HOTFIX: ' + msg)
    self.current_check['result'] = "HOTFIX"

  def assert_table_entry(self, tableName, fieldName, expectedValue):
    """ Accumulates all fixes that a test performs
    so that we can print them all in a single line by
    invoking the log_results() method.

    Usage example:
    fb.assert_table_entry('post', 'isFixedPitch', 1)
    fb.assert_table_entry('OS/2', 'fsType', 0)
    fb.log_results("Something test.")
    """

    # This is meant to support multi-level field hierarchy
    fields = fieldName.split('.')
    obj = self.font[tableName]
    for f in range(len(fields)-1):
      obj = getattr(obj, fields[f])
    field = fields[-1]
    value = getattr(obj, field)

    if value != expectedValue:
      setattr(obj, field, expectedValue)
      self.fixes.append("{} {} from {} to {}".format(tableName,
                                                     fieldName,
                                                     value,
                                                     expectedValue))

  # TODO: "hotfix" and "autofix" are confusing names in here:
  def log_results(self, message, hotfix=True):
    """ Concatenate and log all fixes that happened up to now
    in a good and regular syntax """
    if self.fixes == []:
      self.ok(message)
    else:
      if hotfix:
        if self.config['autofix']:
          self.hotfix("{} Fixes: {}".format(message, " | ".join(self.fixes)))
        else:
          self.error(("{} Changes that must be applied to this font:"
                      " {}").format(message, " | ".join(self.fixes)))
      else:
        self.error("{} {}".format(message, " | ".join(self.fixes)))

      # empty the buffer of fixes,
      # in preparation for the next test
      self.fixes = []
