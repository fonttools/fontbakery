# coding: utf-8

from flask import Blueprint, request, flash, g, session, redirect, url_for

from .models import User
from ..extensions import db, github
from flask.ext.babel import gettext as _

gitauth = Blueprint('gitauth', __name__, url_prefix='/auth')

@gitauth.after_request
def after_request(response):
    return response

@gitauth.route('/login')
def login():
    # import ipdb; ipdb.set_trace()
    if session.get('user_id', None) is None:
        redirect_uri = url_for('.authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True)
        params = {'redirect_uri': redirect_uri, 'scope': 'user:email,public_repo'}
        return redirect(github.get_authorize_url(**params))
    else:
        flash('Already logged in')
        return redirect(url_for('frontend.splash'))

@gitauth.route('/callback')
def authorized(next = None):
    next_url = request.args.get('next') or url_for('frontend.splash')

    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(next_url)

    redirect_uri = url_for('.authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)
    auth = github.get_auth_session(data=data)

    token = auth.access_token
    me = auth.get('user').json()

    user = User.get_or_init(me['login'])

    if user.id is None:
        # new record isn't saved yet
        flash(_('Welcome to font bakery.'))

    # update user data
    user.name = me['name']
    user.github_access_token = token
    user.avatar = me['gravatar_id']
    user.email = me['email']

    # save to database
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    session['token'] = token
    g.user = user
    print(user.id)
    flash('You were signed in')

    return redirect(next_url)

@gitauth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('frontend.splash'))

