import pkgutil
import fontbakery
from fontbakery.utils import get_theme
from importlib import import_module
from fontbakery.profile import get_module_profile
import json
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions
import re


def md2html(x):
    return cmarkgfm.markdown_to_html_with_extensions(x, options=cmarkgfmOptions.CMARK_OPT_UNSAFE, extensions=["autolink"])


checks = {}
profiles_modules = [
    x.name
    for x in pkgutil.walk_packages(fontbakery.__path__, "fontbakery.")
    if x.name.startswith("fontbakery.profiles")
]
for profile_name in profiles_modules:
    imported = import_module(profile_name, package=None)
    profile = get_module_profile(imported)
    if not profile:
        continue
    profile_name = profile_name[20:]
    for section in profile._sections.values():
        for check in section._checks:
            if check.id not in checks:
                checks[check.id] = {
                    "sections": set(),
                    "profiles": set(),
                }
            checks[check.id]["sections"].add(section.name)
            checks[check.id]["profiles"].add(profile_name)
            for attr in ["proposal", "rationale", "severity", "description"]:
                if getattr(check, attr):
                    md = getattr(check, attr)
                    if attr == "rationale":
                        md = re.sub(r"(?m)^\s+", "", md)
                        checks[check.id][attr] = md2html(md)
                    else:
                        checks[check.id][attr] = md

for ck in checks.values():
    ck["sections"] = list(ck["sections"])
    ck["profiles"] = list(ck["profiles"])
print("window.fbchecks=" + json.dumps(checks, indent=4, sort_keys=True))
