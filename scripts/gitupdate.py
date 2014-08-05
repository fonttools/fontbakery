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
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bakery.app import db, github
from bakery.github import GithubSessionAPI, GithubSessionException

from bakery.models import Project, User


def check_for_update(project):
    user = User.query.filter_by(login=project.login).first()
    if not user:
        return
    if not user.github_access_token:
        return
    _github = GithubSessionAPI(github, user.github_access_token)
    try:
        commit = _github.get_latest_commit(project.full_name)
        project.latest_commit = commit['sha'][:7]
        project.last_updated = datetime.datetime.now()
        db.session.commit()
    except GithubSessionException:
        pass


def main():
    date = datetime.datetime.now() - datetime.timedelta(minutes=20)

    projects = Project.query.filter_by(is_github=True)
    projects = projects.filter(Project.last_updated < date)
    for project in projects:
        check_for_update(project)


if __name__ == '__main__':
    main()
