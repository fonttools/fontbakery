DEBUG = True
SECRET_KEY = '\xa8\xad%\x07kL\x8f\x04D\xf4\xbf"\xe0a\xb52\x1d\xb2\xf3\xe9\xf7\xcfag'

SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite'
CELERY_BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'
CELERY_RESULT_DBURI = "sqla+sqlite:///celerydb.sqlite"
CELERY_ANNOTATIONS = {"*": {"rate_limit": "10/s"}}
# echo enables verbose logging from SQLAlchemy.
CELERY_RESULT_ENGINE_OPTIONS = {"echo": True}

# default babel values
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'
ACCEPT_LANGUAGES = ['en']

# make sure that you have started debug mail server using command
# $ make mail

MAIL_SERVER = 'locahost'
MAIL_PORT = 20025
MAIL_USE_SSL = False
MAIL_USERNAME = 'm@xen.ru'
#MAIL_PASSWORD = 'topsecret'

# github app data
GITHUB_CONSUMER_KEY = '4a1a8295dacab483f1b5'
GITHUB_CONSUMER_SECRET = 'ec494ff274b5a5c7b0cb7563870e4a32874d93a6'

# flatpages
FLATPAGES_EXTENSION = '.md'
import os
FLATPAGES_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs')

del os