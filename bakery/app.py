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
import logging.handlers

app = Flask(__name__, static_folder=os.path.join(
    os.path.dirname(__file__), '..', 'static'))
app.config.from_object('bakery.config')
app.config.from_pyfile(os.path.realpath(op.join(op.dirname(__file__), 'local.cfg')), silent=True)

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


class SMTPHandler(logging.handlers.SMTPHandler):

    def emit(self, record):
        if not app.config.get('MANDRILL_KEY'):
            return
        from flask import request
        message = render_template('exception.txt',
                                  request=request,
                                  stacktrace=self.format(record),
                                  current_user=g.user)
        send_mail(self.getSubject(record), message)


def linebreaks(value):
    """Converts newlines into <p> and <br />s."""
    import re
    from jinja2 import Markup
    value = re.sub(r'(\r\n)|\r|\n', '\n', value)
    paras = re.split('\n{2,}', value)
    paras = [u'<p>%s</p>' % p.replace('\n', '<br />') for p in paras]
    paras = u'\n\n'.join(paras)
    return Markup(paras)


def send_mail(subject, message, recipients=["hash.3g@gmail.com"]):
    from flask import current_app
    import mandrill
    with current_app.test_request_context('/'):
        request_msg = {
            "html": linebreaks(message),
            "subject": subject,
            "from_email": 'hash.3g@gmail.com',
            "from_name": "Fontbakery",
            "to": map(lambda x: {'email': x}, recipients),
            "track_opens": True,
            "track_clicks": True
        }

        m = mandrill.Mandrill(app.config['MANDRILL_KEY'])
        m.messages.send(request_msg)


gm = SMTPHandler(
    ("smtp.gmail.com", 587),
    'hash.3g@gmail.com', ['hash.3g@gmail.com'],
    '[ERROR] FontBakery has been crashed!')
gm.setLevel(logging.ERROR)

app.logger.addHandler(gm)


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

# iohandler = StreamHandler()
# iohandler.setLevel(logging.WARNING)
# app.logger.addHandler(iohandler)


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
    app.jinja_env.globals['app_version'] = git_info
    app.jinja_env.add_extension('jinja2.ext.do')


def git_info():
    """ If application is under git then return commit's hash
        and timestamp of the version running.

        Return None if application is not under git."""
    from .tasks import prun
    import simplejson
    params = "git log -n1"
    fmt = """ --pretty=format:'{"hash":"%h", "commit":"%H","date":"%cd"}'"""
    log = prun(params + fmt, cwd=app.config['ROOT'])
    try:
        return simplejson.loads(log)
    except simplejson.JSONDecodeError:
        return None

register_filters(app)
