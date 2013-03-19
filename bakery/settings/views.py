# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, g

from ..extensions import github
from ..decorators import login_required
from .models import ProjectCache

settings = Blueprint('settings', __name__, url_prefix='/settings')

@login_required
@settings.route('/', methods=['GET'])
def repos():
    _repos = None
    cache = ProjectCache.query.filter_by(login=g.user.login).first()
    return render_template('settings/repos.html', cache=cache)

@login_required
@settings.route('/update', methods=['POST'])
def update():
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('settings/repos.html', repos=_repos)


@login_required
@settings.route('/profile', methods=['GET', 'POST'])
def profile():
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('settings/repos.html', repos=_repos)

@login_required
@settings.route('/addhook', methods=['POST'])
def addhook():
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('settings/repos.html', repos=_repos)

