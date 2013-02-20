# -*- coding: utf-8 -*-
"""
    Github Example
    --------------

    Shows how to authorize users with Github.
"""
from bakery.app import app, db, celery, mail, github
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    github_access_token = db.Column(db.Integer)

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

# @app.after_request
# def after_request(response):
#     db_session.remove()
#     return response

@app.route('/')
def index():
    return 'Hello!'

@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token

@app.route('/oauth/callback')
@github.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('index')
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

@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(callback_url=url_for('authorized'))
    else:
        return 'Already logged in'

@app.route('/orgs/<name>')
def orgs(name):
    if github.has_org_access(name):
        return 'Heck yeah he does!'
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

