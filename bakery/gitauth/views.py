# coding: utf-8

from flask import Blueprint, render_template, request, flash, g, session, redirect, url_for

from .models import User
from ..extensions import db, github
from flask.ext.babel import gettext as _

from ..tasks import add_together

gitauth = Blueprint('gitauth', __name__, url_prefix='/auth')

# @gitauth.before_request
# def before_request():
#     print(session)
#     g.user = None
#     if 'user_id' in session:
#         g.user = User.query.get(session['user_id'])

@gitauth.after_request
def after_request(response):
    return response

@github.tokengetter
def token_getter():
    user = g.user
    if user is not None:
        return (user.github_access_token, '')

@gitauth.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(callback = url_for('gitauth.authorized',
            next=request.args.get('next') or request.referrer or None, _external=True))
    else:
        return 'Already logged in'

@gitauth.route('/settings')
def settings():
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
        flash(_('You denied the request to sign in.'), 'error')
        return redirect(next_url)

    token = resp['access_token']
    user = User.query.filter_by(github_access_token=token).first()

    #1st time
    if user is None:
        flash(_('Welcome to font bakery.'))
        user = User(token)
        session['user_id'] = user.id

    user.github_access_token = token
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    g.user = user
    print(user.id)
    flash('You were signed in')
    add_together(1, 1)
    user_info = github.get('/user')

    saved_user = User.query.filter_by(login=user_info.data['login']).first()
    if saved_user:
        # ouch this user already was here, probably has revked access and give
        # it back again
        saved_user.name = user_info.data['name']
        saved_user.avatar = user_info.data['gravatar_id']
        saved_user.email = user_info.data['email']
        saved_user.github_access_token = token
        db.session.delete(user)
        db.session.add(saved_user)
        db.session.commit()
        user = saved_user
    else:
        # user already in our database, so lets update data
        user.login = user_info.data['login']
        user.name = user_info.data['name']
        user.avatar = user_info.data['gravatar_id']
        user.email = user_info.data['email']
        user.github_access_token = token
        db.session.add(user)
        db.session.commit()

    return redirect(next_url)

@gitauth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('frontend.splash'))

