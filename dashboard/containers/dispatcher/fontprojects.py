#!/usr/bin/env python
import csv
import urllib
CACHE_CSV = "fontprojects.csv"

def get_repos():
  handle = open(CACHE_CSV)
  repos = []
  for row in csv.reader(handle):
    if not row:
      continue
    repos.append(row)
  return repos

git_repos = get_repos()

if __name__ == '__main__':
  PROJECTS_CSV = "https://docs.google.com/spreadsheets/d/1ampzD9veEdrwUMkOAJkMNkftqtv1jEygiPR0wZ6eNl8/pub?gid=0&single=true&output=csv"
  handle = urllib.urlopen(PROJECTS_CSV)
  open(CACHE_CSV, "w").write(handle.read())
  git_repos = get_repos()

  repos_by_status = {}
  for repo in git_repos:
    status = repo[0]
    if status not in repos_by_status.keys():
      repos_by_status[status] = [repo]
    else:
      repos_by_status[status].append(repo)

  total = 0
  enabled = 0
  print ("Number of font repositories in this file:")
  for status in repos_by_status.keys():
    quantity = len(repos_by_status[status])
    print ('"{}": {}'.format(status, quantity))
    total += quantity
    if status in ["OK", "NOTE"]:
      enabled += quantity
  print (('From the total of {} repos,'
          ' {} are enabled.\nEnabled means: "OK" or "NOTE" status.\n').format(total, enabled))
