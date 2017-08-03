#!/usr/bin/env python
import matplotlib
from matplotlib.dates import date2num
import json
from dateutil.parser import parse
import matplotlib.pyplot as plt

import sys
if len(sys.argv) == 1:
  import os
  files = []
  for f in os.listdir("."):
    if f[-14:] == ".burndown.json":
      files.append(f)
elif len(sys.argv) == 2:
  files = [sys.argv[1]]
else:
  usage = ("Usage: {} examplefont.ttf.burndown.json\n"
           "\n"
           "Without attributes the script will target all TTF files"
           " found in the current directory.").format(sys.argv[0])
  sys.exit(usage)

max_val = 0
for target in files:
  data = json.loads(open(target).read())

  values = []
  datetimes = []
  for entry in data["entries"]:
    # example: "Wed May 25 20:07:11 2016 -0400"
    date = parse(entry["date"])
    datetimes.append(parse(entry["date"]))
    values.append(entry["summary"]["Errors"])

  max_val = max(max_val, max(values))
  plt.plot_date(date2num(datetimes), values, '-')

plt.grid(True)
plt.ylim([0, 1.2*max_val])
matplotlib.pyplot.show()
