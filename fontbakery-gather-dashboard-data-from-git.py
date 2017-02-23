#!/usr/bin/env python

from dateutil import parser
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


def calc_font_stats(results):
  stats = {
    "Total": len(results),
    "Errors": 0,
    "Warnings": 0,
    "Hotfixes": 0,
    "Skipped": 0,
    "Passed": 0
  }
  for r in results:
    if r['result'] not in stats.keys():
      stats[r['result']] = 1
    else:
      stats[r['result']] += 1
  return stats


def update_global_stats(family, font):
  if family['summary'] is None:
    family['summary'] = font
  else:
    for k in family['summary'].keys():
      family['summary'][k] += font[k]


clone(REPO_URL, "checkout")
os.chdir("checkout")
#run(["git", "checkout", "master"])
print ("We're now at master branch.")

lines = run(["git", "log", "--oneline", "."]).strip().split('\n')
commits = [line.split()[0].strip() for line in lines]
print ("The commits we'll iterate over are: {}".format(commits))

r.connect('db', 28015).repl()
try:
  r.db_create('fontbakery').run()
  r.db('fontbakery').table_create('check_results').run()
  r.db('fontbakery').table_create('cached_stats').run()
except:
  # OK, database and tables already exist.
  pass

db = r.db('fontbakery')

for i, commit in enumerate(commits):
  run(["git", "checkout", commit])

  if 1:
#  try:
    print ("[{} of {}] Running fontbakery on commit '{}'...".format(i+1, len(commits), commit))

    datestr = run(['git',
                   'log',
                   '-1',
                   '--pretty=format:\"%cd\"'])
    print ("datestr = {}".format(datestr))
    date = parser.parse(datestr, fuzzy=True)
#  except:
#    print ("Failed to parse commit date string")
#    continue

  try:
    files = get_filenames()
    run(["python", "/fontbakery-check-ttf.py", "--verbose", "--json"] + files)

    family_stats = {
      "giturl": REPO_URL,
      "date": date,
      "summary": None,
      "HEAD": (i==0)
    }
    for f in os.listdir(FONTS_DIR):
      if f[-20:] != ".ttf.fontbakery.json":
        continue

      fname = f.split('.fontbakery.json')[0]
      familyname = fname.split('-')[0]
      family_stats['familyname'] = familyname
      data = open(FONTS_DIR + "/" + f).read()
      results = json.loads(data)
      font_stats = calc_font_stats(results)
      update_global_stats(family_stats, font_stats)
      check_results = {
        "giturl": REPO_URL,
        "results": results,
        "commit": commit,
        "fontname": fname,
        "familyname": familyname,
        "date": date,
        "stats": font_stats,
        "HEAD": (i==0)
      }
      if db.table('check_results').filter({"commit": commit, "fontname":fname}).count().run() == 0:
        db.table('check_results').insert(check_results).run()
      else:
        db.table('check_results').filter({"commit": commit, "fontname":fname}).update(check_results).run()

    if db.table('cached_stats').filter({"giturl": REPO_URL}).count().run() == 0:
      db.table('cached_stats').insert(family_stats).run()
    else:
      db.table('cached_stats').filter({"giturl": REPO_URL}).update(family_stats).run()
  except:
    print("Failed to run fontbakery on this commit (perhaps TTF files moved to a different folder.)")

