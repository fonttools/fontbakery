# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, render_template, request, flash, g, redirect, url_for

from ..extensions import github, db
from ..decorators import login_required
from .models import ProjectCache
from ..project.models import Project

settings = Blueprint('settings', __name__, url_prefix='/settings')

@login_required
@settings.route('/', methods=['GET'])
def repos():
    _repos = None
    cache = ProjectCache.query.filter_by(login=g.user.login).first()
    myprojects = Project.query.filter_by(login=g.user.login).all()
    p = {}
    if myprojects:
        for i in myprojects:
            p[i.full_name] = i
    #import ipdb; ipdb.set_trace()
    return render_template('settings/repos.html', cache=cache, projects=p)

@login_required
@settings.route('/update', methods=['POST'])
def update():
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
            cache = ProjectCache.query.filter_by(login=g.user.login).first()
            if not cache:
                cache = ProjectCache()
                cache.login = g.user.login

            cache.data = _repos
            cache.updated = datetime.datetime.utcnow()

            db.session.add(cache)
            db.session.commit()
            flash('Repositories refreshed.')
        else:
            flash('Unable to load repos list.')
    return redirect(url_for('settings.repos'))


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
@settings.route('/addhook', methods=['GET'])
def addhook(full_name=''):
    z = request
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('settings/repos.html', repos=_repos)

@login_required
@settings.route('/delhook', methods=['GET'])
def addhook(full_name=''):
    z = request
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash('Unable to load repos list.')
    return render_template('settings/repos.html', repos=_repos)
