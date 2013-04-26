# -*- coding: utf-8 -*-
import datetime
import json
import logging
from flask.ext.babel import gettext as _

from flask import Blueprint, render_template, request, flash, g, redirect, url_for, session

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
    auth = github.get_session(token = session['token'])
    if g.user is not None:
        resp = auth.get('/user/repos', data = {'type': 'public'})
        if resp.status_code == 200:
            _repos = resp.json()
            cache = ProjectCache.query.filter_by(login=g.user.login).first()
            if not cache:
                cache = ProjectCache()
                cache.login = g.user.login

            cache.data = _repos
            cache.updated = datetime.datetime.utcnow()

            db.session.add(cache)
            db.session.commit()
            flash(_('Repositories refreshed.'))
        else:
            flash(_('Unable to load repos list.'))
    return redirect(url_for('settings.repos'))

@login_required
@settings.route('/profile', methods=['GET', 'POST'])
def profile():
    auth = github.get_session(token = session['token'])
    _repos = None
    if g.user is not None:
        resp = auth.get('/user/repos', data = {'type': 'public'})
        if resp.status_code == 200:
            _repos = resp.json()
        else:
            flash(_('Unable to load repos list.'))
    return render_template('settings/repos.html', repos=_repos)

HOOK_URL = 'http://requestb.in/nrgo4inr'

@login_required
@settings.route('/addhook/<path:full_name>') #, methods=['GET'])
def addhook(full_name):
    auth = github.get_session(token = session['token'])
    old_hooks = auth.get('/repos/%s/hooks' % full_name)
    if old_hooks.status_code != 200:
        logging.error('Repos API reading error for user %s' % g.user.login)
        flash(_('Github API access error, please try again later'))
        return redirect(url_for('settings.repos'))

    exist_id = False
    if old_hooks.json():
        for i in old_hooks.json():
            if i.has_key('name') and i['name'] == 'web':
                if i.has_key('config') and i['config'].has_key('url') \
                    and i['config']['url'] == HOOK_URL:
                    exist_id = i['id']

    if exist_id:
        logging.warn('Delete old webhook for user %s, repo %s and id %s' % (g.user.login, full_name, exist_id))
        resp = auth.delete('/repos/%(full_name)s/hooks/%(id)s' % {'full_name': full_name, 'id': exist_id})
        if resp.status_code != 204:
            flash(_('Error deleting old webhook, delete if manually or retry'))
            return redirect(url_for('settings.repos'))

    resp = auth.post('/repos/%(full_name)s/hooks' % {'full_name': full_name},
        data = json.dumps({
            'name':'web',
            'active': True,
            'events': ['push'],
            'config': {
                'url': HOOK_URL,
                'content_type': 'json',
                'secret': '11' # TODO: sign from name and SECRET.
            }
         })
    )
    if resp.status_code < 300: # no errors, in 2xx range
        project = Project.query.filter_by(login = g.user.login, full_name = full_name).first()
        if not project:
            project = Project(
                login = g.user.login, 
                full_name = full_name,
            )
        project_data = auth.get('/repos/%s' % full_name)
        if project_data.status_code == 200:
            project.cache_update(data = project_data.json())
        else:
            flash(_('Repository information update error'))
            return redirect(url_for('settings.repos'))
        db.session.add(project)
        db.session.commit()
    else:
        logging.error('Web hook registration error for %s' % full_name)
        flash(_('Repository webhook update error'))
        return redirect(url_for('settings.repos'))

    flash(_('Added webhook for %s.' % (full_name)))
    return redirect(url_for('settings.repos'))

@login_required
@settings.route('/delhook/<path:full_name>', methods=['GET'])
def delhook(full_name):
    auth = github.get_session(token = session['token'])

    old_hooks = auth.get('/repos/%s/hooks' % full_name)
    print(old_hooks.content)
    if old_hooks.status_code != 200:
        logging.error('Repos API reading error for user %s' % g.user.login)
        flash(_('Github API access error, please try again later'))
        return redirect(url_for('settings.repos'))

    exist_id = False
    if old_hooks.json():
        for i in old_hooks.json():
            if i.has_key('name') and i['name'] == 'web':
                if i.has_key('config') and i['config'].has_key('url') \
                    and i['config']['url'] == HOOK_URL:
                    exist_id = i['id']

    if exist_id:
        resp = auth.delete('/repos/%(full_name)s/hooks/%(id)s' % {'full_name': full_name, 'id': exist_id})
        if resp.status_code != 204:
            flash(_('Error deleting old webhook, delete if manually or retry'))
    else:
        flash(_("Webhook is not registered on github, probably it was deleted manually"))

    project = Project.query.filter_by(login = g.user.login, full_name = full_name).first()

    if project:
        db.session.delete(project)
        db.session.commit()

    return redirect(url_for('settings.repos'))
