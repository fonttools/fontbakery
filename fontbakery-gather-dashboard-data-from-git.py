#!/usr/bin/env python

import glob
import json
import os
import rethinkdb as r
import subprocess
import sys

prefix_elements = os.environ.get("FONTFILE_PREFIX", "").split('/')
FONTS_PREFIX = prefix_elements.pop(-1)
FONTS_DIR = '/'.join(prefix_elements)
REPO_URL = os.environ.get("GIT_REPO_URL")

def run(cmd):
  output = None
  try:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError, e:
    print ("Error: {}".format(e))
    pass
  except OSError:
    print("could not execute command '{}' !".format(cmd))
    pass


def get_filenames():
  files = []
  for f in os.listdir(FONTS_DIR):
    pref = f[:len(FONTS_PREFIX)]
    if f[-4:] == ".ttf" and pref == FONTS_PREFIX:
      files.append(FONTS_DIR + "/" + f)
  if len(files) == 0:
    print ("Where are the TTF files?!\n")
  else:
    print ("We'll be checking these files:\n{}\n".format("\n".join(files)))
  return files


def clone(repo, clone_dir, depth=None):
  if depth is None:
    run(["git", "clone", repo, clone_dir])
  else:
    run(["git", "clone", repo, "--depth={}".format(depth), clone_dir])

if REPO_URL == None:
  print("Usage: This container expects to receive a mandatory"
        " git repo URL in the GIT_REPO_URL environment variable.")
  sys.exit(-1)

clone(REPO_URL, "checkout")
os.chdir("checkout")
#run(["git", "checkout", "master"])
print ("We're now at master branch.")

lines = run(["git", "log", "--oneline", "."]).strip().split('\n')
commits = [line.split()[0].strip() for line in lines]

r.connect('db', 28015).repl()
try:
  r.db_create('fontbakery').run()
except:
  # OK, it already exists
  pass

try:
  r.db('fontbakery').table_create('checkresults').run()
except:
  # alright!
  pass

db = r.db('fontbakery')

#cursor = r.table("fontprojects").filter(r.row["repo_url"] == repo_url).run()
#for project in cursor:
#  pass  # TODO!

already_checked_revisions = []
# TODO: fetch from database

for commit in commits:
  if commit in already_checked_revisions:
    del(commit)

print ("The commits we'll iterate over are: {}".format(commits))

for i, commit in enumerate(commits):
  run(["git", "checkout", commit])

  try:
    print ("[{} of {}] Running fontbakery on commit '{}'...".format(i+1, len(commits), commit))
    date = run(["git", 
               "log",  # display the commid id and message 
               "HEAD~1..HEAD"]  # only for the last commit
    ).split('\n')[2].split("Date:")[1].strip()
  except:
    print ("Failed to parse commit date string")
    continue

  try:
    files = get_filenames()
    run(["python", "/fontbakery-check-ttf.py", "--verbose", "--json"] + files)

    for f in os.listdir(FONTS_DIR):
      if f[-20:] != ".ttf.fontbakery.json":
        continue

      fname = f.split('.fontbakery.json')[0]
      data = open(FONTS_DIR + "/" + f).read()
      check_results = {
        "giturl": REPO_URL,
        "results": json.loads(data),
        "commit": commit,
        "fontname": fname,
        "date": date
      }
      if db.table('checkresults').filter({"commit": commit, "fontname":fname}).count().run() == 0:
        db.table('checkresults').insert(check_results).run()
      else:
        db.table('checkresults').filter({"commit": commit, "fontname":fname}).update(check_results).run()
  except:
    print("Failed to run fontbakery on this commit (perhaps TTF files moved to a different folder.)")

