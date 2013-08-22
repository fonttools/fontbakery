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

import sys, os
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from bakery import create_app, init_app
from bakery.models import FontStats
from bakery.extensions import db

app = create_app(app_name='bakery')
app.config['DEBUG'] = True
app.config.from_object('config')
app.config.from_pyfile('local.cfg', silent=True)
init_app(app)

ctx = app.test_request_context('/')
ctx.push()

r = requests.get('http://www.google.com/fonts/stats?key=WebFonts2010')

if r.status_code != 200:
    print("Wrong download code", file=sys.stderr)
    sys.exit(1)

soup = BeautifulSoup(r.text)

c = soup.find('div', 'container')

for i in c.find_all('div', 'row')[1:]:
    family, total, month, week, yesterday, rate = [k.text for k in i.find_all('div', 'column')]

    s = FontStats.query.filter_by(family=str(family).lower()).first()
    if not s:
        s = FontStats()

    s.family = str(family).lower()
    s.total = int(total.replace(',',''))
    s.month = int(month.replace(',',''))
    s.week = int(week.replace(',',''))
    s.yesterday = int(yesterday.replace(',',''))
    s.rate = float(rate)

    db.session.add(s)

db.session.commit()

ctx.pop()

