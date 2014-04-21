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
#pylint:disable-msg=W0612
import logging
import os
import os.path as op

from flask import Flask, request, render_template, g, session
from logging import StreamHandler


app = Flask(__name__, static_folder=os.path.join(
    os.path.dirname(__file__), '..', 'static'))
app.config.from_object('config')
app.config.from_pyfile(op.join(op.dirname(__file__), 'local.cfg'), silent=True)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask.ext.mail import Mail
mail = Mail(app)

from rauth.service import OAuth2Service

github = OAuth2Service(
    name='github',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_id=app.config['GITHUB_CONSUMER_KEY'],
    client_secret=app.config['GITHUB_CONSUMER_SECRET']
)

from flask_flatpages import FlatPages
pages = FlatPages(app)

from flask.ext.rq import RQ
rq = RQ(app)

from flask.ext.babel import Babel
babel = Babel(app)


@app.errorhandler(403)
def forbidden_page(error):
    return render_template("misc/403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("misc/404.html"), 404


@app.errorhandler(500)
def server_error_page(error):
    return render_template("misc/500.html"), 500


@app.before_request
def guser():
    g.user = None
    if 'user_id' in session:
        if session['user_id']:
            #pylint:disable-msg=E1101
            from gitauth.models import User
            user = User.query.get(session['user_id'])
            if user:
                g.user = user
            else:
                del session['user_id']


@app.before_request
def gdebug():
    if app.debug:
        g.debug = True
    else:
        g.debug = False


@babel.localeselector
def get_locale():
    if g.user:
        if hasattr(g.user, 'ui_lang'):
            return g.user.ui_lang

    accept_languages = app.config.get('ACCEPT_LANGUAGES')
    return request.accept_languages.best_match(accept_languages)

iohandler = StreamHandler()
iohandler.setLevel(logging.WARNING)
app.logger.addHandler(iohandler)


def register_blueprints(app):
    from .gitauth import gitauth
    from .frontend import frontend
    from .realtime import realtime
    from .api import api
    from .settings import settings
    from .project import project
    app.register_blueprint(gitauth)
    app.register_blueprint(frontend)
    app.register_blueprint(realtime)
    app.register_blueprint(settings)
    app.register_blueprint(api)
    app.register_blueprint(project)


def register_filters(app):
    # Additional Jinja filters
    from utils import pretty_date, signify

    app.jinja_env.filters['pretty_date'] = pretty_date
    app.jinja_env.filters['signify'] = signify
    app.jinja_env.add_extension('jinja2.ext.do')

register_filters(app)
