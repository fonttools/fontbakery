# -*- coding: utf-8 -*-
from flask import config

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from celery import Celery
celery = Celery()

from flask.ext.oauth import OAuth
oauth = OAuth()

github = oauth.remote_app('github',
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    consumer_key='4a1a8295dacab483f1b5',
    # I know it is awful but I dunno how to make it right way
    consumer_secret=open('gitsecret', 'r').readlines()[0]
)

from flask_flatpages import FlatPages
pages = FlatPages()