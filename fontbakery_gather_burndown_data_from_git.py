#!/usr/bin/env python

import subprocess

def run(cmd):
  output = None
  try:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError, e:
    pass
  except OSError:
    print("could not execute command '{}' !".format(cmd))
    pass

import glob
import sys
files = None
if len(sys.argv) < 2:
  print ("usage: {} files.ttf".format(sys.argv[0]))
  sys.exit(-1)
else:
  fontfile_prefix = sys.argv[1]

import os
files = []
for f in os.listdir("."):
  pref = f[:len(fontfile_prefix)]
  if f[-4:] == ".ttf" and pref == fontfile_prefix:
    files.append(f)

print ("\nWe'll be checking these files:\n{}\n\n".format("\n".join(files)))

run(["git", "checkout", "master"])
print ("We're now at master branch.")

cmd = ["git", "log", "--oneline", "."]
lines = run(cmd).strip().split('\n')
commits = [line.split()[0].strip() for line in lines]
print ("The commits we'll iterate over are: {}".format(commits))

print ("Running fontbakery on master...")
fontbakery_cmd = ["/home/felipe/devel/github_felipesanches/fontbakery/fontbakery-check-ttf.py"] + files
print ("This is our fontbakery command:\n'{}'".format(fontbakery_cmd))

for i, commit in enumerate(commits):
  run(["git", "checkout", commit])
#  print "Checked out '{}'!".format(commit)
  print ("[{} of {}] Running fontbakery on commit '{}'...".format(i+1, len(commits), commit))
  run(fontbakery_cmd)

print("We're done! Check the burndown.json files now.")

