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

import os
from flask import Flask, request, render_template, g, session

from .extensions import db, mail, pages, rq, babel #, celery

# blueprints
from .gitauth import gitauth
from .frontend import frontend
from .realtime import realtime
from .api import api
from .settings import settings
from .project import project
# For import *
__all__ = ['create_app', 'init_app']


def create_app(app_name=__name__):
    # Flask application constructor. Doesn't init extensions and blueprints
    # because caller can use its own configuration.

    app = Flask(app_name, static_folder = os.path.join(
        os.path.dirname(__file__), '..', 'static') )
    return app


def init_app(app):
    # Register all blueprints and init extensions.
    import logging
    from logging import StreamHandler
    iohandler = StreamHandler()
    iohandler.setLevel(logging.WARNING)
    app.logger.addHandler(iohandler)

    app.register_blueprint(gitauth)
    app.register_blueprint(frontend)
    app.register_blueprint(realtime)
    app.register_blueprint(settings)
    app.register_blueprint(api)
    # keep it last
    app.register_blueprint(project)

    extensions_fabrics(app)
    error_pages(app)
    gvars(app)
    register_filters(app)


def extensions_fabrics(app):
    # All extensions should have .init_app method to allow divide instancing
    # and application object register.
    db.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    pages.init_app(app)
    rq.init_app(app)
    # github.init_app(app)


def error_pages(app):
    # HTTP error pages definitions

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("misc/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("misc/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("misc/500.html"), 500


def gvars(app):
    # Place to register project-wide global variables.
    from gitauth.models import User

    @app.before_request
    def guser():
        g.user = None
        if 'user_id' in session:
            if session['user_id']:
                #pylint:disable-msg=E1101
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


def register_filters(app):
    # Additional Jinja filters
    from utils import pretty_date, signify

    app.jinja_env.filters['pretty_date'] = pretty_date
    app.jinja_env.filters['signify'] = signify
    app.jinja_env.add_extension('jinja2.ext.do')
