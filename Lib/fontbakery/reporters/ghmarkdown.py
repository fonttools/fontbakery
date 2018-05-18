# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals, division

from future import standard_library
standard_library.install_aliases()
from builtins import map
import os
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.checkrunner import Status

LOGLEVELS=["ERROR","FAIL","WARN","SKIP","INFO","PASS"]


class GHMarkdownReporter(SerializeReporter):

  def __init__(self, loglevels, **kwd):
    super(GHMarkdownReporter, self).__init__(**kwd)
    self.loglevels = loglevels


  def emoticon(self, name):
    return {
      'ERROR': ':broken_heart:',
      'FAIL': ':fire:',
      'WARN': ':warning:',
      'INFO': ':information_source:',
      'SKIP': ':zzz:',
      'PASS': ':bread:',
    }[name]


  def html5_collapsible(self, summary, details):
    return ("<details>\n"
            "<summary>{}</summary>\n"
            "{}\n"
            "</details>\n").format(summary, details)


  def log_md(self, log):
    if not self.omit_loglevel(log["status"]):
      return "* {} **{}** {}\n".format(self.emoticon(log["status"]),
                                       log["status"],
                                       log["message"])
    else:
      return ""


  def check_md(self, check):
    checkid = check["key"][1].split(":")[1].split(">")[0]

    check["logs"].sort(key=lambda c: c["status"])
    logs = "".join(map(self.log_md, check["logs"]))
    github_search_url = ("[{}](https://github.com/googlefonts/fontbakery/"
                         "search?q={})").format(checkid, checkid)
    return self.html5_collapsible("{} <b>{}:</b> {}".format(self.emoticon(check["result"]),
                                                            check["result"],
                                                            check["description"]),
                                  "\n* {}\n{}".format(github_search_url, logs))

  def omit_loglevel(self, msg):
    return self.loglevels and (self.loglevels[0] > Status(msg))

  def get_markdown(self):
    checks = {}
    family_checks = []
    data = self.getdoc()
    num_checks = 0
    for section in data["sections"]:
      for cluster in section["checks"]:
        if not isinstance(cluster, list):
          cluster = [cluster]
        num_checks += len(cluster)
        for check in cluster:
          if self.omit_loglevel(check["result"]):
            continue

          if "filename" not in check.keys():
            # That's a family check!
            family_checks.append(check)
          else:
            key = os.path.basename(check["filename"])
            if key not in checks:
              checks[key] = []
            checks[key].append(check)

    md = "## Fontbakery report\n\n"

    if family_checks:
      family_checks.sort(key=lambda c: c["result"])
      md += self.html5_collapsible("<b>[{}] Family checks</b>".format(len(family_checks)),
                                   "".join(map(self.check_md, family_checks)) + "<br>")

    for filename in checks.keys():
      checks[filename].sort(key=lambda c: LOGLEVELS.index(c["result"]))
      md += self.html5_collapsible("<b>[{}] {}</b>".format(len(checks[filename]),
                                                           filename),
                                   "".join(map(self.check_md, checks[filename])) + "<br>")

    if num_checks != 0:
      summary_table = "### Summary\n\n" + \
                      ("| {} " + " | {} ".join(LOGLEVELS) + " |\n").format(*[self.emoticon(k) for k in LOGLEVELS]) + \
                      ("|:-----:|:----:|:----:|:----:|:----:|:----:|\n"
                       "| {} | {} | {} | {} | {} | {} |\n"
                       "").format(*[data["result"][k] for k in LOGLEVELS]) +\
                      ("| {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% |\n"
                       "").format(*[100*data["result"][k]/num_checks for k in LOGLEVELS])
      md += "\n" + summary_table

    omitted = [l for l in LOGLEVELS if self.omit_loglevel(l)]
    if omitted:
      md += "\n" + \
            "**Note:** The following loglevels were omitted in this report:\n" + \
            "".join(map("* **{}**\n".format, omitted))

    return md
