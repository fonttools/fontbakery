# coding: utf-8

from flask import Blueprint, render_template, request, flash, g, session, redirect, url_for

from .models import User
from ..extensions import db, github

gitauth = Blueprint('gitauth', __name__, url_prefix='/auth')

# @gitauth.before_request
# def before_request():
#     print(session)
#     g.user = None
#     if 'user_id' in session:
#         g.user = User.query.get(session['user_id'])

@gitauth.after_request
def after_request(response):
    # db_session.remove()
    return response

@github.tokengetter
def token_getter():
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret

@gitauth.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(callback = url_for('gitauth.authorized',
            next=request.args.get('next') or request.referrer or None, _external=True))
    else:
        return 'Already logged in'

@gitauth.route('/settings')
def index():
    repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('user/settings.html', repos=repos)

@gitauth.route('/callback')
@github.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('frontend.splash')
    if resp is None:
        return redirect(next_url)

    token = resp['access_token']
    user = User.query.filter_by(github_access_token=token).first()
    if user is None:
        user = User(token)
        session['user_id'] = user.id
    user.github_access_token = token

    session['user_id'] = user.id

    return 'Success'


@gitauth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('frontend.splash'))

