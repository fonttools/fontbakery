# -*- coding: utf-8 -*-
from flask import config

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from celery import Celery
celery = Celery()

# from flask.ext.rauth import RauthOAuth2

# github = RauthOAuth2(
#     name='github',
#     base_url='https://api.github.com/',
#     access_token_url='https://github.com/login/oauth/access_token',
#     authorize_url='https://github.com/login/oauth/authorize'
# )

from rauth.service import OAuth2Service

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