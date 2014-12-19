#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
from __future__ import print_function

import argparse
import ConfigParser
import getpass
import git.config
import json
import os
import requests
import shlex
import subprocess
import sys
import urlparse


GITHUB_API = 'https://api.github.com'
url = urlparse.urljoin(GITHUB_API, 'authorizations')


description = ('Creates .travis.yml file with deploying feature.'
               ' This script expects you have [user] section defined in'
               ' .git/config file, expects you have github repo for git'
               ' directory.')


travis_config = """language: python
before_install:
- sudo add-apt-repository --yes ppa:fontforge/fontforge
- sudo apt-get update -qq
- sudo apt-get install python-fontforge ttfautohint swig
- cp /usr/lib/python2.7/dist-packages/fontforge.* "$HOME/virtualenv/python2.7.8/lib/python2.7/site-packages"
install:
- pip install git+https://github.com/behdad/fontTools.git
- pip install git+https://github.com/googlefonts/fontcrunch.git
- pip install git+https://github.com/googlefonts/fontbakery.git
before_script:
- mkdir -p builds/$TRAVIS_COMMIT
script: (set -o pipefail; PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-build.py . 2>&1 | tee -a    builds/$TRAVIS_COMMIT/buildlog.txt)
after_script:
- PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-report.py builds/$TRAVIS_COMMIT
- rm -rf builds/$TRAVIS_COMMIT/sources
- rm -rf builds/$TRAVIS_COMMIT/build.state.yaml
- PATH=/home/travis/virtualenv/python2.7.8/bin/:$PATH fontbakery-travis-deploy.py
branches:
 only:
 - master"""


parser = argparse.ArgumentParser(description=description)

parser.add_argument('--user', '-u', metavar='github-username')
parser.add_argument('--email', '-e', metavar='github-email')
parser.add_argument('path', help='directory with you git repository')

args = parser.parse_args()

git_config_path = os.path.join(args.path, '.git', 'config')
if not os.path.exists(git_config_path):
    print('.git/config file does not exist. please setup your repo'
          ' before usage.', file=sys.stderr)
    sys.exit(1)


travis_config_path = os.path.join(args.path, '.travis.yml')
if not os.path.exists(travis_config_path):
    print('Creating .travis.yml file... ')
    with open(travis_config_path, 'w') as fp:
        fp.write(travis_config)
    print('Done')


git_config = git.config.GitConfigParser(git_config_path)

try:
    user_name = args.user or git_config.get_value('user', 'name')
except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    user_name = raw_input('Please, enter your username: ')

try:
    user_email = args.email or git_config.get_value('user', 'email')
except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    user_email = raw_input('Please, enter your email: ')

note = git_config.get_value('remote "origin"', 'url')
repourl = urlparse.urlparse(note).path.strip('/').rstrip('.git')

repousername, reponame = repourl.split('/', 1)
note = 'Fontbakery for {}'.format(repourl)

msg = 'Please enter password for user "{}": '
password = getpass.getpass(msg.format(user_name))

print('Fetching Github secure token...')
res = requests.post(url, auth=(user_name, password),
                    data=json.dumps({'note': note}))

j = json.loads(res.text)

if res.status_code >= 400:

    if 'required' not in res.headers.get('x-github-otp', ''):
        msg = j.get('message', '(no error description from server)')
        print('ERROR: {}'.format(msg))
        sys.exit(1)

    otp_code = raw_input('OTP Code Required... ')
    res = requests.post(url, auth=(user_name, password),
                        headers={'X-GitHub-OTP': otp_code},
                        data=json.dumps({'note': note}))

    j = json.loads(res.text)

    if res.status_code >= 400:
        msg = j.get('message', '(no error description from server)')
        errors = filter(lambda error: error.get('code') == 'already_exists',
                        j['errors'])
        if errors:
            print(('Fatal Error: You already have a token for "{}", '
                  'you can find it on your github profile page:'.format(note)))
            print('https://github.com/settings/applications'
                  '#personal-access-tokens')
        else:
            print(msg)
        sys.exit(1)

token = j['token']

commandline = ('travis encrypt GIT_NAME="{}" GIT_EMAIL="{}" GH_TOKEN="{}"'
               ' --add --no-interactive -x;')
commandline = commandline.format(user_name, user_email, token)
p = subprocess.Popen(shlex.split(commandline), cwd=args.path)

print('Adding token to .travis.yml... Done')

finalstep = """
Now ensure https://github.com/{} is enabled on https://travis-ci.org/profile and then add, commit and push your file with:
  git add .travis.yml;
  git commit .travis.yml -m "Adding .travis.yml";
  git push origin master;
And then after the next commit you should find a report at http://{}.github.io/{}
""".format(repourl, repousername, reponame)

print(finalstep)
