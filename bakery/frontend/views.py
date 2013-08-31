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

from flask import (Blueprint, render_template, Response, g, request,
    current_app, send_from_directory, redirect, redirect, url_for)

from ..extensions import pages
from ..project.models import Project

frontend = Blueprint('frontend', __name__)

@frontend.before_request
def before_request():
    # Add to global vars list of the projects owned by current user
    if g.user:
        g.projects = Project.query.filter_by(login=g.user.login).all()

@frontend.route('/')
def splash():
    # Splash page, if user is logged in then show dashboard
    if g.user is None:
        return render_template('splash.html')
    else:
        projects = Project.query.filter_by(login=g.user.login).all()
        return render_template('dashboard.html', repos = projects)


@frontend.route('/docs/', defaults={'path': 'index'})
@frontend.route('/docs/<path:path>/', endpoint='page')
def page(path):
    # Documentation views
    _page = pages.get_or_404(path)
    return render_template('page.html', page=_page)

@frontend.route('/robots.txt')
def static_from_root():
    # Static items
    return send_from_directory(current_app.static_folder, request.path[1:])
