#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Report how many github issues/prs were opened and closed for the google/fonts
repository between two specified dates.

Example:
Issues between 2017-01-01 to 2017-06-01:
python fontbakery-check-gf-github.py <user> <pass> 2017-01-01 2017-06-01

The title and url of each issues/pr can be displayed by using the 
-v, --verbose option.
"""
import requests
from datetime import datetime
from argparse import ArgumentParser


def get_issues_paginate(request_issues, start, end, auth):
  """
  If there are too many issues for one page, iterate through the pages
  to collect them all.
  """
  # get the non paginated issues to start with
  issues = get_issues(request_issues, start, end)

  print 'Getting paginated results, be patient...'
  pages = dict(
      [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
        [link.split(';') for link in
          request_issues.headers['link'].split(',')]])

  while 'last' in pages and 'next' in pages:
    request_issues = requests.get(pages['next'], auth=auth)
    page_issues = get_issues(request_issues, start, end)

    for issue_type in page_issues:
      issues[issue_type] = issues[issue_type] + page_issues[issue_type]

    if pages['next'] == pages['last']:
      break
  return issues


def get_issues(request_issues, start, end):
  """
  Return a dictionary containing 3 categories of issues
  """
  issues = [i for i in request_issues.json()]
  return {
    "closed_issues": [
      i for i in issues
      if i['closed_at'] and 'pull_request' not in i
      and iso8601_to_date(i['closed_at']) <= end
    ],

    "opened_issues": [
      i for i in issues
      if not i['closed_at'] and 'pull_request' not in i
      and iso8601_to_date(i['created_at']) >= start
      and iso8601_to_date(i['created_at']) <= end
    ],

    "closed_prs": [
      i for i in issues
      if i['closed_at'] and 'pull_request' in i
      and iso8601_to_date(i['closed_at']) >= start
      and iso8601_to_date(i['closed_at']) <= end
    ],

    "opened_prs": [
      i for i in issues
      if not i['closed_at'] and 'pull_request' in i
      and iso8601_to_date(i['created_at']) >= start
      and iso8601_to_date(i['created_at']) <= end
    ],
  }


def output_issues(issues, key):
  for issue in issues[key]:
    title = issue['title'][:50] + '...'
    url = issue['url'].replace('api.github.com/repos/', 'github.com/')
    print '%s\t%s\t%s' % (
      key,
      title.ljust(50, ' '),
      url,
    )


def iso8601_to_date(date_string):
  """Note, this function will strip out the time and tz"""
  date_string = date_string.split('T')[0]
  return datetime.strptime(date_string, "%Y-%m-%d")


def main():
  parser = ArgumentParser(description=__doc__)
  parser.add_argument('username',
                      help="Your Github username")
  parser.add_argument('password',
                      help="Your Github password")
  parser.add_argument('start',
                      help="Start date in ISO 8601 format YYYY-MM-DD")
  parser.add_argument('end',
                      help="End date in ISO 8601 format YYYY-MM-DD")
  parser.add_argument('-v', '--verbose', action='store_true',
                      help="Output all title and urls for prs and issues")
  parser.add_argument('-ci', '--closed-issues',action='store_true',
                      help="Output all closed issues")
  parser.add_argument('-oi', '--opened-issues',action='store_true',
                      help="Output all opened issues")
  parser.add_argument('-cp', '--closed-pulls',action='store_true',
                      help="Output all closed/merged pull requests")
  parser.add_argument('-op', '--opened-pulls',action='store_true',
                      help="Output all opened pull requests")

  args = parser.parse_args()

  start = iso8601_to_date(args.start)
  end = iso8601_to_date(args.end)

  if start > end:
    raise ValueError('start time is greater than end time')

  repo_url = "https://api.github.com/repos/google/fonts/issues"
  
  request_params = {
    'state': 'all',
    'direction': 'asc',
    'since': args.start,
    'per_page': 100
  }

  auth = (args.username, args.password)
  request_issues = requests.get(
    "https://api.github.com/repos/google/fonts/issues",
    auth=auth,
    params=request_params,
  )

  # Check if issues span more than one page
  if 'link' in request_issues.headers:
    issues = get_issues_paginate(request_issues, start, end, auth)
  else:
    issues = get_issues(request_issues, start, end)

  if args.verbose:
    output_issues(issues, 'closed_issues')
    output_issues(issues, 'opened_issues')
    output_issues(issues, 'closed_prs')
    output_issues(issues, 'opened_prs')
  else:
    if args.closed_issues:
      output_issues(issues, 'closed_issues')
    if args.opened_issues:
      output_issues(issues, 'opened_issues')
    if args.closed_pulls:
      output_issues(issues, 'closed_prs')
    if args.opened_pulls:
      output_issues(issues, 'opened_prs')

  print 'Issues closed\t%s' % len(issues['closed_issues'])
  print 'Issues opened\t%s' % len(issues['opened_issues'])
  print 'Pull requests closed/merged\t%s' % len(issues['closed_prs'])
  print 'Pull requests opened\t%s' % len(issues['opened_prs'])


if __name__ == '__main__':
  main()
