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
from flask import Blueprint, g

from ..models import Project, ProjectBuild

api = Blueprint('api', __name__)


@api.route('/webhook/<path:project_id>')
def webhook(project_id):
    # Make it more secure and check for in request header X-Hub-Signature
    # It should have HMAC of payload body and secret key
    # request.args.get('payload')
    # secret key is project signify(full_path)
    p = Project.query.filter_by(login=g.user.login, id=project_id)
    p = p.first_or_404()
    ProjectBuild.make_build(p, revision='HEAD', force_sync=True)
    return "Ok"


@api.route('/updateall')
def updateall():

    all = Project.query.all()
    for p in all:
        p.sync()

    return "Ok"
