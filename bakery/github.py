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
from flask.ext.babel import gettext as _


class GithubSessionException(Exception):
    """ Exception raised by GithubSessionAPI """

    def __init__(self, message):
        self.message = message


class GithubSessionAPI:

    def __init__(self, github_session, usertoken):
        self._session = github_session.get_session(usertoken)

    def get_latest_commit(self, fullname):
        resp = self._session.get('repos/%s/commits' % fullname)
        if resp.status_code == 200:
            return resp.json()[0]
        else:
            raise GithubSessionException(_(('Could not connect to Github'
                                            ' to load repo data.')))

    def get_repo_data(self, fullname):
        print fullname
        resp = self._session.get('repos/%s' % fullname)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise GithubSessionException(_(('Could not connect to Github'
                                            ' to load repo data.')))

    def get_repo_list(self):
        """ Returns list of repos for user token """
        page = 0
        _repos = []
        while True:
            resp = self._session.get('/user/repos?per_page=100&page=%s' % page,
                                     data={'type': 'all'})
            if resp.status_code == 200:
                _repos.extend(resp.json())
                if len(resp.json()) == 100:
                    page = page + 1
                    continue
            else:
                raise GithubSessionException(_(('Could not connect to Github'
                                                ' to load repos list.')))
            break

        orgs = self._session.get('/user/orgs')
        if orgs.status_code == 200:
            for x in orgs.json():
                opage = 0
                while True:
                    url = '/orgs/%s/repos?per_page=100&page=%s'
                    oresp = self._session.get(url % (x['login'], opage),
                                              data={'type': 'all'})
                    if oresp.status_code == 200:
                        _repos.extend(oresp.json())
                        if len(oresp.json()) == 100:
                            opage = opage + 1
                            continue
                    else:
                        msg = _(('Error get repos for organization'
                                 ' %(login)s'), login=x['login'])
                        raise GithubSessionException(msg)
                    break

        return _repos
