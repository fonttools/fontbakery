# -*- coding: utf-8 -*-
from flask import config

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from celery import Celery
celery = Celery()

from flask.ext.rauth import RauthOAuth2

github = RauthOAuth2(
    name='github',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

from flask_flatpages import FlatPages
pages = FlatPages()