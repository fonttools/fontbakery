# coding: utf-8

from flask import Flask, request, render_template
from flaskext.babel import Babel

from .extensions import db, mail, celery, oauth, github
from .gitauth import gitauth
from .frontend import frontend

# For import *
__all__ = ['create_app']


def create_app(app_name=__name__):

    app = Flask(app_name)
    app.register_blueprint(gitauth)
    app.register_blueprint(frontend)

    extensions_fabrics(app)
    error_pages(app)


    return app

def extensions_fabrics(app):
    db.init_app(app)
    mail.init_app(app)
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)

    celery.config_from_object(app.config)

    global github
    github = oauth.remote_app('github',
        base_url='https://api.github.com/',
        request_token_url='https://api.twitter.com/oauth/request_token',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        consumer_key=app.config.get('GITHUB_CLIENT_ID'),
        consumer_secret=app.config.get('GITHUB_SECRET')
    )



def error_pages(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("pages/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("pages/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("pages/500.html"), 500
