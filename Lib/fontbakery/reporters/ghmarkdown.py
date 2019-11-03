import os
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.checkrunner import Status
from fontbakery import __version__ as version

LOGLEVELS=["ERROR","FAIL","WARN","SKIP","INFO","PASS","DEBUG"]


class GHMarkdownReporter(SerializeReporter):

  def __init__(self, loglevels, **kwd):
    super(GHMarkdownReporter, self).__init__(**kwd)
    self.loglevels = loglevels


  def emoticon(self, name):
    return {
      'ERROR': "\U0001F494", # 💔  :broken_heart:
      'FAIL':  "\U0001F525", # 🔥  :fire:
      'WARN':  "\U000026A0", # ⚠️  :warning:
      'INFO':  "\U00002139", # ℹ️  :information_source:
      'SKIP':  "\U0001F4A4", # 💤  :zzz:
      'PASS':  "\U0001F35E", # 🍞  :bread
      'DEBUG': "\U0001F50E", # 🔎 :mag_right:
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


  def render_rationale(self, check, checkid):
    if not "rationale" in check:
      return ""

    # Ideally we'll at some point invoke a proper markdown
    # parser here. But for now, let's simply fill the raw
    # content into an 80-column block of text and output it
    # enclosed in <pre></pre> tags...
    import html
    from fontbakery.utils import text_flow, unindent_rationale
    content = unindent_rationale(check['rationale'], checkid)
    rationale = html.escape(text_flow(content, 80))
    return f"<pre>--- Rationale ---\n{rationale}</pre>\n"

  def check_md(self, check):
    checkid = check["key"][1].split(":")[1].split(">")[0]
    profile = check["profile"]

    check["logs"].sort(key=lambda c: c["status"])
    logs = "".join(map(self.log_md, check["logs"]))
    github_search_url = (f"[{checkid}]"
                          "(https://font-bakery.readthedocs.io/en/latest"
                         f"/fontbakery/profiles/{profile}.html#{checkid})")

    rationale = self.render_rationale(check, checkid)

    return self.html5_collapsible("{} <b>{}:</b> {}".format(self.emoticon(check["result"]),
                                                            check["result"],
                                                            check["description"]),
                                  f"\n* {github_search_url}\n{rationale}\n{logs}")

  def omit_loglevel(self, msg):
    return self.loglevels and (self.loglevels[0] > Status(msg))


  def deduce_profile_from_section_name(self, section):
    # This is very hacky!
    # We should have a much better way of doing it...
    if 'Google Fonts' in section: return 'googlefonts'
    if 'Adobe' in section: return 'adobefonts'
    if 'Universal' in section: return 'universal'
    if 'Basic UFO checks' in section: return 'ufo_sources'
    if 'Checks inherited from Microsoft Font Validator' in section: return 'fontval'
    if 'fontbakery.profiles.' in section: return section.split('fontbakery.profiles.')[1].split('>')[0]
    return section


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

          check['profile'] = self.deduce_profile_from_section_name(section["key"][0])
          if "filename" not in check.keys():
            # That's a family check!
            family_checks.append(check)
          else:
            key = os.path.basename(check["filename"])
            if key not in checks:
              checks[key] = []
            checks[key].append(check)

    md = "## Fontbakery report\n\n"
    md += f"Fontbakery version: {version}\n\n"

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
                      ("|:-----:|:----:|:----:|:----:|:----:|:----:|:----:|\n"
                       "| {} | {} | {} | {} | {} | {} | {} |\n"
                       "").format(*[data["result"][k] for k in LOGLEVELS]) +\
                      ("| {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% | {:.0f}% |\n"
                       "").format(*[100*data["result"][k]/num_checks for k in LOGLEVELS])
      md += "\n" + summary_table

    omitted = [l for l in LOGLEVELS if self.omit_loglevel(l)]
    if omitted:
      md += "\n" + \
            "**Note:** The following loglevels were omitted in this report:\n" + \
            "".join(map("* **{}**\n".format, omitted))

    return md
