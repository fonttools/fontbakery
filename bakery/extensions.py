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

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from rauth.service import OAuth2Service

# Because of restrictions of OAuth2Service this lines can't be moved to config.py
GITHUB_CLIENT_ID = '4a1a8295dacab483f1b5'
GITHUB_CLIENT_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'

github = OAuth2Service(
    name='github',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_id= GITHUB_CLIENT_ID,
    client_secret= GITHUB_CLIENT_SECRET,
)

from flask_flatpages import FlatPages
pages = FlatPages()

from flask.ext.rq import RQ
rq = RQ()

from flask.ext.babel import Babel
babel = Babel()
