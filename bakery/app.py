# coding: utf-8

from flask import Flask, request, render_template, g, session
from flaskext.babel import Babel

from .extensions import db, mail, pages, rq #, celery

# blueprints
from .gitauth import gitauth
from .frontend import frontend
from .realtime import realtime
from .api import api
from .settings import settings
from .project import project
# For import *
__all__ = ['create_app']

def create_app(app_name=__name__):

    app = Flask(app_name)
    return app

def init_app(app):
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
    db.init_app(app)
    mail.init_app(app)
    babel = Babel(app)
    pages.init_app(app)
    rq.init_app(app)
    # github.init_app(app)

    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)

def error_pages(app):
    # define error pages

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
    from gitauth.models import User

    @app.before_request
    def before_request():
        g.user = None
        if 'user_id' in session:
            if session['user_id']:
                user = User.query.get(session['user_id'])
                if user:
                    g.user = user
                else:
                    del session['user_id']

def register_filters(app):
    from utils import pretty_date

    app.jinja_env.filters['pretty_date'] = pretty_date

