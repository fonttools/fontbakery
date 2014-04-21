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

DEBUG = True
BACKGROUND = True
SECRET_KEY = '\xa8\xad%\x07kL\x8f\x04D\xf4\xbf"\xe0a\xb52\x1d\xb2\xf3\xe9\xf7\xcfag'

from os.path import dirname, abspath

SQLALCHEMY_DATABASE_URI = 'sqlite:////%s/data.sqlite' % dirname(abspath(__file__))
# CELERY_BROKER_URL = 'redis://localhost:6379',
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# # CELERY_BROKER_URL = 'sqla+sqlite:////%s/celerydb.sqlite' % dirname(abspath(__file__))
# # CELERY_RESULT_DBURI = "sqla+sqlite:////%s/celerydb.sqlite" % dirname(abspath(__file__))
# CELERY_ANNOTATIONS = {"*": {"rate_limit": "10/s"}}
# # echo enables verbose logging from SQLAlchemy.
# CELERY_RESULT_ENGINE_OPTIONS = {"echo": True}

# default babel values
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'
ACCEPT_LANGUAGES = ['en']

# make sure that you have started debug mail server using command
# $ make mail

MAIL_SERVER = 'localhost'
MAIL_PORT = 20025
MAIL_USE_SSL = False
MAIL_USERNAME = 'm@xen.ru'
#MAIL_PASSWORD = 'topsecret'

# github app data
GITHUB_CONSUMER_KEY = '4a1a8295dacab483f1b5'
GITHUB_CONSUMER_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'

GITAUTH_LOGIN_LIST = ['offline', ]
# flatpages
FLATPAGES_EXTENSION = '.md'
import os
FLATPAGES_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'docs')
DATA_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
ROOT = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), '..')

HOOK_URL = 'http://bakery.fontforge.org/api/webhook/{id}'


del os
