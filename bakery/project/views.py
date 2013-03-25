# coding: utf-8
try:
    import simplejson as json
except ImportError:
    import json

from flask import Blueprint, render_template, Response

from ..extensions import db

project = Blueprint('project', __name__)

# @app.route('/user/<username>')
# def show_user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     return render_template('show_user.html', user=user)


@project.route('/<username>/')
def user(username):
    return render_template('project/user.html')

@project.route('/<username>/<repo>/')
def repo(username, repo):
    return render_template('project/build.html')

@project.route('/<username>/<repo>/history')
def history(username, repo):
    return render_template('project/history.html')

@project.route('/<username>/<repo>/<int:build_id>')
def build(username, repo, build_id):
    return render_template('project/build.html')

