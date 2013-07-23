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

from flask import Blueprint, request, flash, g, session, redirect, url_for

from .models import User
from ..extensions import db, github
from flask.ext.babel import gettext as _

gitauth = Blueprint('gitauth', __name__, url_prefix='/auth')

@gitauth.after_request
def after_request(response):
    return response

@gitauth.route('/me')
def me():
    # Visit this URL and log the user in as Mikhail's 'xen' username
    # This enables developers to work offline when they have no access to github authentication
    # FOR MULTI USER INSTALLATIONS THIS IS AN EXPLOIT :)
    user = User.get_or_init('xen')
    if user.id == 1:
        # XXX: this is temporary
        session['user_id'] = user.id
        g.user = user
        flash('Welcome!')

    return redirect(url_for('frontend.splash'))

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

    # if user.id is None:
    #     new record isn't saved yet
    #     flash(_('Welcome to Bakery.'))

    # update user data
    user.name = me.get('name', me.get('login'))
    user.github_access_token = token
    user.avatar = me['gravatar_id']
    user.email = me['email']

    # save to database
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    g.user = user
    flash('Welcome!')

    return redirect(next_url)

@gitauth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('frontend.splash'))

