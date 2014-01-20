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

import datetime
from giturlparse import parse
import logging
from flask.ext.babel import gettext as _

from flask import (Blueprint, render_template, request, flash, g, redirect,
                    url_for, json)

from ..extensions import github, db
from ..decorators import login_required
from .models import ProjectCache
from ..project.models import Project

settings = Blueprint('settings', __name__, url_prefix='/settings')


@settings.route('/', methods=['GET'])
@login_required
def repos():
    # pylint:disable-msg=E1101
    cache = ProjectCache.query.filter_by(login=g.user.login).first()
    myprojects = Project.query.filter_by(
        login=g.user.login, is_github=True).all()
    mygit = Project.query.filter_by(login=g.user.login, is_github=False).all()

    p = {}
    if myprojects:
        for i in myprojects:
            p[i.full_name] = i
    # import ipdb; ipdb.set_trace()
    return render_template('settings/index.html',
                           cache=cache,
                           projects=p,
                           gitprojects=mygit
                           )


@settings.route('/update', methods=['POST'])
@login_required
def update():
    """Update the list of the user's githib repos"""
    auth = github.get_session(token=g.user.token)
    if g.user is not None:
        if g.user.login != u'offline':
            page = 0
            _repos = []
            while True:
                resp = auth.get('/user/repos?per_page=100&page=%s' % page, data={'type': 'all'})
                if resp.status_code == 200:
                    _repos.extend(resp.json())
                    if len(resp.json()) == 100:
                        page = page + 1
                        continue
                else:
                    flash(_('Could not connect to Github to load repos list.'))
                break
            orgs = auth.get('/user/orgs')
            if orgs.status_code == 200:
                for x in orgs.json():
                    opage = 0
                    while True:
                        oresp = auth.get('/orgs/%s/repos?per_page=100&page=%s' % (x['login'], opage), data={'type': 'all'})
                        if oresp.status_code == 200:
                            _repos.extend(oresp.json())
                            if len(oresp.json()) == 100:
                                opage = opage + 1
                                continue
                        else:
                            flash(_('Error get repos for organization %(login)s', login=x['login']))
                        break

            if _repos:
                cache = ProjectCache.query.filter_by(login=g.user.login).first()
                if not cache:
                    cache = ProjectCache()
                    cache.login = g.user.login
                cache.data = _repos
                # note the time
                cache.updated = datetime.datetime.utcnow()
                # add the cache to the database
                db.session.add(cache)
                db.session.commit()
                flash(_('Repositories refreshed.'))
        else:
            flash(_('Offline user has no Github account.'))
    else:
        flash(_('No user found.'))
    return redirect(url_for('settings.repos') + "#tab_massgithub")


@settings.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    auth = github.get_session(token=g.user.token)
    _repos = None
    if g.user is not None:
        resp = auth.get('/user/repos', data={'type': 'public'})
        if resp.status_code == 200:
            _repos = resp.json()
        else:
            flash(_('Unable to load repos list.'))
    return render_template('settings/index.html', repos=_repos)

HOOK_URL = 'http://requestb.in/nrgo4inr'


@settings.route('/addhook/<path:full_name>')  # , methods=['GET'])
@login_required
def addhook(full_name):
    auth = github.get_session(token=g.user.token)
    old_hooks = auth.get('/repos/%s/hooks' % full_name)
    if old_hooks.status_code != 200:
        logging.error('Repos API reading error for user %s' % g.user.login)
        flash(_('GitHub API access error, please try again later'))
        return redirect(url_for('settings.repos') + "#tab_github")

    exist_id = False
    if old_hooks.json():
        for i in old_hooks.json():
            if i.has_key('name') and i['name'] == 'web':
                if i.has_key('config') and i['config'].has_key('url') \
                        and i['config']['url'] == HOOK_URL:
                    exist_id = i['id']

    if exist_id:
        logging.warn('Delete old webhook for user %s, repo %s and id %s' %
                     (g.user.login, full_name, exist_id))
        resp = auth.delete('/repos/%(full_name)s/hooks/%(id)s' %
                           {'full_name': full_name, 'id': exist_id})
        if resp.status_code != 204:
            flash(_('Error deleting old webhook, delete if manually or retry'))
            return redirect(url_for('settings.repos') + "#tab_github")

    resp = auth.post('/repos/%(full_name)s/hooks' % {'full_name': full_name},
                     data=json.dumps({
                                     'name': 'web',
                                     'active': True,
                                     'events': ['push'],
                                     'config': {
                                     'url': HOOK_URL,
                                     'content_type': 'json',
                                     'secret': '11'  # TODO: sign from name and SECRET.
                                     }
                                     })
                     )
    if resp.status_code < 300:  # no errors, in 2xx range
        project = Project.query.filter_by(
            login=g.user.login, full_name=full_name).first()
        if not project:
            project = Project(
                login=g.user.login,
                full_name=full_name,
                # TODO: Use actual github clone string used by Github
                # clone='git@github.com:%s/%s.git' % (g.user.login, full_name),
                clone='git://github.com/%s.git' % full_name,
                is_github=True
            )
        project_data = auth.get('/repos/%s' % full_name)
        if project_data.status_code == 200:
            project.cache_update(data=project_data.json())
        else:
            flash(_('Repository information update error'))
            return redirect(url_for('settings.repos') + "#tab_github")
        project.is_github = True
        db.session.add(project)
        db.session.commit()
    else:
        logging.error('Web hook registration error for %s' % full_name)
        flash(_('Repository webhook update error'))
        return redirect(url_for('settings.repos') + "#tab_github")

    flash(_('Added webhook for %(name)s.', name=full_name))
    project.build()
    return redirect(url_for('settings.repos') + "#tab_github")


@settings.route('/delhook/<path:full_name>', methods=['GET'])
@login_required
def delhook(full_name):
    auth = github.get_session(token=g.user.token)

    old_hooks = auth.get('/repos/%s/hooks' % full_name)
    if old_hooks.status_code != 200:
        logging.error('Repos API reading error for user %s' % g.user.login)
        flash(_('GitHub API access error, please try again later'))
        return redirect(url_for('settings.repos') + "#tab_github")

    exist_id = False
    if old_hooks.json():
        for i in old_hooks.json():
            if i.has_key('name') and i['name'] == 'web':
                if i.has_key('config') and i['config'].has_key('url') \
                        and i['config']['url'] == HOOK_URL:
                    exist_id = i['id']

    if exist_id:
        resp = auth.delete('/repos/%(full_name)s/hooks/%(id)s' %
                           {'full_name': full_name, 'id': exist_id})
        if resp.status_code != 204:
            flash(_('Error deleting old webhook: Delete it manually, or retry'))
    else:
        flash(_("Webhook is not registered on Github, it was probably deleted manually"))

    # pylint:disable-msg=E1101
    project = Project.query.filter_by(
        login=g.user.login, full_name=full_name).first()

    if project:
        db.session.delete(project)
        db.session.commit()

    return redirect(url_for('settings.repos') + "#tab_github")


@settings.route('/addclone', methods=['POST'])
@login_required
def addclone():
    # According url schemes here http://git-scm.com/docs/git-push it is
    # near impossibru to validate url, so just check if its length is > 10
    # (let it be 10)
    #
    # TODO in the future, use http://schacon.github.io/git/git-ls-remote.html to validate the URL string
    # http://stackoverflow.com/questions/9610131/how-to-check-the-validity-of-a-remote-git-repository-url
    #
    # TODO we could do very light validation that the form field is not 0 in JS
    # TODO we could do very light validation of the URL in JS
    clone = request.form.get('clone')
    if len(clone) == 0:
        flash(_('Enter a URL.'))
        return redirect(url_for('frontend.splash'))

    # pylint:disable-msg=E1101
    dup = Project.query.filter_by(login=g.user.login, is_github=False, clone=clone).first()
    if dup:
        flash(_("This repository is a duplicate"))

    if not parse(clone).valid:
        flash(_("Problem parsing git url"))
        return redirect(url_for('settings.repos') + "#tab_massgithub")

    project = Project(
        login=g.user.login,
        clone=clone,
        is_github=False)

    if project:
        db.session.add(project)
        db.session.commit()

    flash(_("Repository successfully added. Wait for its download and complete setup"))
    project.sync()
    return redirect(url_for('frontend.splash'))


@settings.route('/delclone/<int:project_id>', methods=['GET'])
@login_required
def delclone(project_id):
    # pylint:disable-msg=E1101
    project = Project.query.filter_by(
        login=g.user.login, id=project_id).first()
    if not project:
        flash(_("Project not found."))
        return redirect(url_for('frontend.splash'))
    db.session.delete(project)
    db.session.commit()
    flash(_("Repository %(pid)s succesfuly removed (but files remain on the server)", pid=project_id))
    return redirect(url_for('frontend.splash'))


@settings.route('/massgit/', methods=['POST'])
@login_required
def massgit():
    git_ids = request.form.getlist('git')
    # pylint:disable-msg=E1101
    projects = Project.query.filter_by(
        login=g.user.login, is_github=True).all()

    pfn = {}
    for p in projects:
        if p.full_name not in git_ids:
            db.session.delete(p)
            flash(_("Repository %(name)s successfully removed (but files remain on the server)", name=p.full_name))
        pfn[p.full_name] = p

    db.session.commit()
    for gid in git_ids:
        if not pfn.get(gid):
            project = Project(
                login=g.user.login,
                full_name=gid,
                # TODO: Use actual github clone string used by Github
                # clone='git@github.com:%s/%s.git' % (g.user.login, full_name),
                clone='git://github.com/%s.git' % gid,
                is_github=True
            )
            db.session.add(project)
            db.session.commit()
            flash(_("Repository successfully added. Wait for its download and complete setup"))
            project.sync()

    db.session.commit()
    return redirect(url_for('settings.repos') + "#tab_massgithub")


@settings.route('/batch', methods=['POST'])
@login_required
def batch():
    # pylint:disable-msg=E1101
    urls = request.form.get('urls', '') + "\n"  # this makes m
    n = 0
    for l in urls.split("\n"):
        l = l.strip()
        if not l:
            continue
        if not parse(l).valid:
            flash(_("Url %(url)s isn't accepted, parse error", url=l))
        else:
            dup = Project.query.filter_by(login=g.user.login,
                                            is_github=False, clone=l).first()

            if dup:
                flash(_("Url %(url)s is duplicate", url=l))
            else:
                project = Project(login=g.user.login, clone=l, is_github=False)

                if project:
                    db.session.add(project)
                    db.session.commit()
                    db.session.refresh(project)

                project.sync()

                n = n + 1

    flash(_("%(num)s repositories successfuly added", num=n))

    return redirect(url_for('settings.repos'))
