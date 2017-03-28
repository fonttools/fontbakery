#!/usr/bin/env python
from __future__ import print_function
from dateutil import parser
import glob
import json
import os
import pika
import rethinkdb as r
import subprocess
import sys
import time

fonts_dir = None
fonts_prefix = None
runs = int(os.environ.get("NONPARALLEL_JOB_RUNS", 1))

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
  for f in os.listdir(fonts_dir):
    pref = f[:len(fonts_prefix)]
    if f[-4:] == ".ttf" and pref == fonts_prefix:
      fullpath = fonts_dir + "/" + f
      # Do we need to escape spaces in the fullpaths here?
      files.append(fullpath)
  if len(files) == 0:
    print ("Where are the TTF files?!\n")
    sys.exit(0)
  else:
    print ("We'll be checking these files:\n{}\n".format("\n".join(files)))
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
  for r in results:
    result = r['result']
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

def perform_job(REPO_URL):
  clone(REPO_URL, "clonedir")
  os.chdir("clonedir")
  run(["git", "checkout", "master"])
  print ("We're now at master branch.")

  lines = run(["git", "log", "--oneline", "."]).strip().split('\n')
  commits = ["master"] + [line.split()[0].strip() for line in lines]
  print ("The commits we'll iterate over are: {}".format(commits))

  db_host = os.environ.get("RETHINKDB_DRIVER_SERVICE_HOST", 'db')
  r.connect(db_host, 28015).repl()
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

    try:
      print ("[{} of {}] Running fontbakery on commit '{}'...".format(i+1, len(commits), commit))

      datestr = run(['git',
                     'log',
                     '-1',
                     '--pretty=format:\"%cd\"'])
      print ("datestr = {}".format(datestr))
      date = parser.parse(datestr, fuzzy=True)
    except:
      print ("Failed to parse commit date string")
      continue

    try:
      files = get_filenames()
      run(["python", "/fontbakery-check-ttf.py", "--verbose", "--json"] + files)

      family_stats = {
        "giturl": REPO_URL,
        "commit": commit,
        "date": date,
        "summary": {"OK": 0,
                    "Total": 0},
        "HEAD": (i==0)
      }
      for f in os.listdir(fonts_dir):
        if f[-20:] != ".ttf.fontbakery.json":
          continue
        print ("Check results JSON file: {}".format(f))

        fname = f.split('.fontbakery.json')[0]
        familyname = fname.split('-')[0]
        family_stats['familyname'] = familyname
        data = open(fonts_dir + "/" + f).read()
        results = json.loads(data)
        font_stats = calc_font_stats(results)
        update_global_stats(family_stats['summary'], font_stats)
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
        #print ("check_results: {}".format(check_results))

        if db.table('check_results').filter({"commit": commit, "fontname":fname}).count().run() == 0:
          db.table('check_results').insert(check_results).run()
        else:
          db.table('check_results').filter({"commit": commit, "fontname":fname}).update(check_results).run()

      if db.table('cached_stats').filter({"commit":commit, "giturl": REPO_URL}).count().run() == 0:
        db.table('cached_stats').insert(family_stats).run()
      else:
        db.table('cached_stats').filter({"commit":commit, "giturl": REPO_URL}).update(family_stats).run()
    except:
      print("Failed to run fontbakery on this commit (perhaps TTF files moved to a different folder.)")
      break


connection = None
def callback(ch, method, properties, body):
  global fonts_dir, fonts_prefix, runs
  msg = json.loads(body)
  print("Received %r" % msg, file=sys.stderr)
  repo_url = msg["GIT_REPO_URL"]
  if '/' in msg["FONTFILE_PREFIX"]:
    prefix_elements = msg["FONTFILE_PREFIX"].split('/')
    fonts_prefix = prefix_elements.pop(-1)
    fonts_dir = '/'.join(prefix_elements)
  else:
    fonts_prefix = msg["FONTFILE_PREFIX"]
    fonts_dir = '.'
  perform_job(repo_url)
  ch.basic_ack(delivery_tag = method.delivery_tag)
  connection.close()
  runs -= 1
  if runs == 0:
    sys.exit(0)


def main():
  global connection
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
      pass

main()

