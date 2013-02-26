# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from celery import Celery
celery = Celery()

from flask.ext.oauth import OAuth
from flask.ext.github import GithubAuth
# github doesn't support class fabric so data is hardcoded
github = GithubAuth(
    client_id=None,
    client_secret=None,
    session_key='user_id'
)