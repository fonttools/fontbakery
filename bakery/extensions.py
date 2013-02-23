# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from celery import Celery
celery = Celery()

# from flask.ext.github import GithubAuth
# github = GithubAuth()
