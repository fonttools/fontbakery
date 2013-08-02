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

try:
    import simplejson as json
except ImportError:
    import json

from flask import Blueprint, render_template, Response, g, request, current_app, send_from_directory
from flask.ext.babel import gettext as _

from ..extensions import pages
from ..project.models import Project
from ..tasks import check_yaml, project_state_get

frontend = Blueprint('frontend', __name__)

@frontend.before_request
def before_request():
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()

@frontend.route('/')
def splash():
    if g.user is None:
        return render_template('splash.html')
    else:
        projects = Project.query.filter_by(login=g.user.login).all()
        repos = []
        for i in projects:
            repos.append({
                'id': i.id,
                'clone': i.clone,
                'yaml': check_yaml(login = g.user.login, project_id = i.id),
                'state': project_state_get(login = g.user.login, project_id = i.id)
                })

        return render_template('dashboard.html', repos = repos)

@frontend.route('/docs/', defaults={'path': 'about'})
@frontend.route('/docs/<path:path>/', endpoint='page')
def page(path):
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)

@frontend.route('/quicksearch', methods=['GET', 'POST'])
def quicksearch():
    return Response(json.dumps(['xen/font', 'dave/font', 'xen/font2']))

@frontend.route('/robots.txt')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])
