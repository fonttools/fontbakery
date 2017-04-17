#!/usr/bin/env python
from __future__ import print_function
from dateutil import parser
import json
import os
import pika
import rethinkdb as r
import subprocess
import sys
import time
import urllib

runs = int(os.environ.get("NONPARALLEL_JOB_RUNS", 1))
MAX_NUM_ITERATIONS = 1 # For now we'll limit the jobs to run
                       # up to "MAX_NUM_ITERATIONS" commits
                       # in the font project repos

REPO_URL = None
FAMILYNAME = None
db = None

def run(cmd):
  try:
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError, e:
    print ("Error: {}".format(e))
  except OSError:
    print("could not execute command '{}' !".format(cmd))


def get_filenames(fonts_dir, fonts_prefix):
  files = []
  for f in os.listdir(fonts_dir):
    pref = f[:len(fonts_prefix)]
    if f[-4:] == ".ttf" and pref == fonts_prefix:
      fullpath = fonts_dir + "/" + f
      # Do we need to escape spaces in the fullpaths here?
      files.append(fullpath)
  return files


def clone(repo, clone_dir, depth=None):
  if depth is None:
    run(["git", "clone", repo, clone_dir])
  else:
    run(["git", "clone", repo, "--depth={}".format(depth), clone_dir])


def calc_font_stats(results):
  stats = {
    "Total": len(results),
    "OK": 0
  }
  for res in results:
    result = res['result']
    if result not in stats.keys():
      stats[result] = 1
    else:
      stats[result] += 1
  return stats


def update_global_stats(summary, stats):
  for k in stats.keys():
    if k in summary.keys():
      summary[k] += stats[k]
    else:
      summary[k] = stats[k]

def save_output_on_database(commit, output):
  data = {"commit": commit, "familyname": FAMILYNAME, "output": output}
  print ("save_output_on_database: '{}' [{}]".format(FAMILYNAME, commit))
  if db.table('fb_log').filter({"commit": commit, "familyname": FAMILYNAME}).count().run() == 0:
    db.table('fb_log').insert(data).run()
  else:
    db.table('fb_log').filter({"commit": commit, "familyname": FAMILYNAME}).update(data).run()


def save_results_on_database(f, fonts_dir, commit, i, family_stats, date):
#  print ("Invoked 'save_results_on_database' with f='{}'".format(f))
  if f[-20:] != ".ttf.fontbakery.json":
#    print("Not a report file.")
    return

  print ("Check results JSON file: {}".format(f))
  fname = f.split('.fontbakery.json')[0]
  family_stats['familyname'] = FAMILYNAME
  data = open(fonts_dir + "/" + f).read()
  results = json.loads(data)
  font_stats = calc_font_stats(results)
  update_global_stats(family_stats['summary'], font_stats)
  check_results = {
    "giturl": REPO_URL,
    "results": results,
    "commit": commit,
    "fontname": fname,
    "familyname": FAMILYNAME,
    "date": date,
    "stats": font_stats,
    "HEAD": (i==0)
  }

  if db.table('check_results').filter({"commit": commit, "fontname":fname}).count().run() == 0:
    db.table('check_results').insert(check_results).run()
  else:
    db.table('check_results').filter({"commit": commit, "fontname":fname}).update(check_results).run()


def infer_date_from_git():
  try:
    datestr = run(['git',
                   'log',
                   '-1',
                   '--pretty=format:\"%cd\"'])
    print ("datestr = {}".format(datestr))
    return parser.parse(datestr, fuzzy=True)
  except:
    print ("Failed to parse commit date string")
    return None


def save_overall_stats_to_database(commit, family_stats):
  print ("save_overall_stats_to_database:\nstats = {}".format(family_stats))
  if db.table('cached_stats').filter({"commit":commit, "giturl": REPO_URL, "familyname": FAMILYNAME}).count().run() == 0:
    db.table('cached_stats').insert(family_stats).run()
  else:
    db.table('cached_stats').filter({"commit":commit, "giturl": REPO_URL, "familyname": FAMILYNAME}).update(family_stats).run()


# Returns boolean "success"
def run_fontbakery_on_commit(fonts_dir, fonts_prefix, commit, i):
  date = infer_date_from_git()
  files = get_filenames(fonts_dir, fonts_prefix)
  if len(files) > 0:
    print ("We'll be checking these files:\n{}\n".format("\n".join(files)))
  else:
    print ("No font files were found.")
    return False

  output = run(["python", "/fontbakery-check-ttf.py", "--verbose", "--json"] + files)
  save_output_on_database(commit, output)

  family_stats = {
    "familyname": FAMILYNAME,
    "giturl": REPO_URL,
    "commit": commit,
     "date": date,
    "summary": {"OK": 0,
                "Total": 0},
    "HEAD": (i==0)
  }

  for f in os.listdir(fonts_dir):
    save_results_on_database(f, fonts_dir, commit, i, family_stats, date)

  save_overall_stats_to_database(commit, family_stats)
  return True

def checkout_and_test_git_repo(fonts_dir, fonts_prefix):
  global db
  clone(REPO_URL, "clonedir", depth=MAX_NUM_ITERATIONS)
  os.chdir("clonedir")
  run(["git", "checkout", "master"])
  print ("We're now at master branch.")

  lines = run(["git", "log", "--oneline", "."]).strip().split('\n')
  commits = ["master"] + [line.split()[0].strip() for line in lines]
  print ("The commits we'll iterate over are: {}".format(commits))

  for i, commit in enumerate(commits):
    print ("[{} of {}] Checking out commit '{}'".format(i+1, len(commits), commit))
    run(["git", "checkout", commit])
    print ("==> Running fontbakery on commit '{}'...".format(commit))
    run_fontbakery_on_commit(fonts_dir, fonts_prefix, commit, i)


def run_fontbakery_on_production_files():
  PROD_URL = "https://fonts.google.com/download?family={}".format(FAMILYNAME)
  os.mkdir("prod")
  open("prod/family.zip", "w+").write(urllib.urlopen(PROD_URL).read())
  output = run(["unzip", "prod/family.zip", "-d", "prod"])
  print("unzip output: {}".format(output))
  files = []
  for f in os.listdir("prod"):
    if f[-4:] == ".ttf":
      fullpath = "prod/" + f
      # Do we need to escape spaces in the fullpaths here?
      files.append(fullpath)

  if len(files) == 0:
    print ("Could not find production files for '{}'".format(FAMILYNAME))
    return False

  print ("We'll check the following PRODUCTION font files: {}".format(files))
  output = run(["python", "/fontbakery-check-ttf.py", "--verbose", "--json"] + files)
  save_output_on_database("prod", output)

  commit = "prod" # This is sort of a hack!

  family_stats = {
    "familyname": FAMILYNAME,
    "giturl": REPO_URL,
    "commit": commit,
    "date": None,
    "summary": {"OK": 0,
                "Total": 0},
    "HEAD": False
  }

  for f in os.listdir("prod"):
    save_results_on_database(f, "prod", commit, -1, family_stats, None)

  save_overall_stats_to_database(commit, family_stats)
  return True


connection = None
def callback(ch, method, properties, body): #pylint: disable=unused-argument
  global runs, REPO_URL, FAMILYNAME
  msg = json.loads(body)
  print("Received %r" % msg, file=sys.stderr)

  STATUS = msg["STATUS"]
  REPO_URL = msg["GIT_REPO_URL"]
  FAMILYNAME = msg["FAMILYNAME"]
  fonts_prefix = msg["FONTFILE_PREFIX"]
  fonts_dir = '.'
  if '/' in fonts_prefix:
    prefix_elements = fonts_prefix.split('/')
    fonts_prefix = prefix_elements.pop(-1)
    fonts_dir = '/'.join(prefix_elements)

  run_fontbakery_on_production_files()

  if STATUS == "OK" or STATUS == "NOTE":
    checkout_and_test_git_repo(fonts_dir, fonts_prefix)

  ch.basic_ack(delivery_tag = method.delivery_tag)
  connection.close()

  runs -= 1
  if runs == 0:
    print("Finished work. Shutting down this container instance...")
    sys.exit(0)
  else:
    print("Will fetch another workload...")


def main():
  global connection, db

  db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
  r.connect(db_host, 28015).repl()
  try:
    r.db_create('fontbakery').run()
    r.db('fontbakery').table_create('fb_log').run()
    r.db('fontbakery').table_create('check_results').run()
    r.db('fontbakery').table_create('cached_stats').run()
  except:
    # OK, database and tables already exist.
    pass
  db = r.db('fontbakery')

  while True:
    try:
      msgqueue_host = os.environ.get("RABBITMQ_SERVICE_SERVICE_HOST", os.environ.get("BROKER"))
      connection = pika.BlockingConnection(pika.ConnectionParameters(host=msgqueue_host))
      channel = connection.channel()
      channel.queue_declare(queue='font_repo_queue', durable=True)
      print('Waiting for messages...', file=sys.stderr)
      channel.basic_qos(prefetch_count=1)
      channel.basic_consume(callback,
                            queue='font_repo_queue')
      channel.start_consuming()
    except pika.exceptions.ConnectionClosed:
      print ("RabbitMQ not ready yet.", file=sys.stderr)
      time.sleep(1)

main()

