from flask import Flask
from celery import Celery

from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.github import GithubAuth


def make_celery(_app):
    _celery = Celery(_app.import_name, broker=_app.config['CELERY_BROKER_URL'])
    _celery.conf.update(_app.config)
    TaskBase = _celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    _celery.Task = ContextTask
    return _celery

app = Flask('fontbakery')
app.config.from_object('config')
app.config.from_pyfile('local.cfg', silent=True)
celery = make_celery(app)
db = SQLAlchemy(app)
#Auth(app)
mail = Mail(app)
github = GithubAuth(
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_ID'],
    session_key='user_id'
)
