# -*- coding: utf-8 -*-
import datetime
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
    _repos = None
    if g.user is not None:
        resp = github.get('/user/repos', data = {'type': 'public'})
        if resp.status == 200:
            _repos = resp.data
        else:
            flash(_('Unable to load repos list.'))
    return render_template('settings/repos.html', repos=_repos)

HOOK_URL = 'http://requestb.in/185gvyw1'

@login_required
@settings.route('/addhook/<path:full_name>') #, methods=['GET'])
def addhook(full_name):
    #import ipdb; ipdb.set_trace()
    old_hooks = github.get('/repos/%s/hooks' % full_name)
    if old_hooks.status != 200:
        logging.error('Repos API reading error for user %s' % g.user.login)
        flash(_('Github API access error, please try again later'))
        return redirect(url_for('settings.repos'))

    exist_id = False
    if old_hooks.data:
        for i in old_hooks.data:
            if i.has_key('name') and i['name'] == 'web':
                if i.has_key('config') and i['config'].has_key('url') \
                    and i['config']['url'] == HOOK_URL:
                    exist_id = i['id']

    import ipdb; ipdb.set_trace()
    if exist_id:
        logging.warn('Delete old webhook for user %s, repo %s and id %s' % (g.user.login, full_name, exist_id))
        resp = github.delete('/repos/%(full_name)s/hooks/%(id)s' % {'full_name': full_name, 'id': exist_id})
        if resp.status != 204:
            flash(_('Error deleting old webhook, delete if manually or retry'))
            return redirect(url_for('settings.repos'))

    resp = github.post('/repos/%(full_name)s/hooks' % {'full_name': full_name},
        data = {
            'name':'web',
            'active': True,
            'events': ['push'],
            'config': {
                'url': HOOK_URL,
                'content_type': 'json',
                'secret': '11' # TODO: sign from name and SECRET.
            }
         },
         format = 'json',
         headers = {'Authorization': 'token %s' % (github.make_client(token=None).token.key)}
    )
    if resp.status < 300: # no errors, in 2xx range
        project = Project.query.filter_by(login = g.user.login, full_name = full_name).first()
        if not project:
            project = Project(
                login = g.user.login, 
                full_name = full_name,
            )
        project_data = github.get('/repos/%s' % full_name)
        if project_data.status == 200:
            project.cache_update(data = project_data.data)
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
@settings.route('/delhook', methods=['GET'])
def delhook(full_name=''):
    flash(_('Deleted webhook for %s to list.' % full_name))
    return redirect(url_for('settings.repos'))
