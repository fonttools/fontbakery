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
""" To run this tests use `nosetests tests.test_tasks` from command line """
import os.path as op
import unittest

from mock import MagicMock

from bakery.app import app
from bakery.gitauth.views import authorize_user
from bakery.tasks import get_subsets_coverage_data
from bakery.tasks import refresh_repositories, refresh_latest_commits


class TaskTestCase(unittest.TestCase):

    def test_subsets_coverage_data(self):
        path = op.join(app.config['ROOT'], 'tests/fixtures/Font-Bold.ttf')
        self.assertTrue(get_subsets_coverage_data([path], ''))

        path = op.join(app.config['ROOT'], 'tests/fixtures/Font-Bold.ttx')
        self.assertTrue(get_subsets_coverage_data([path], ''))


class TestRepository(unittest.TestCase):

    def test_execute_refresh_repos_task_after_login(self):
        with app.test_request_context('/'):
            refresh_repositories.delay = MagicMock(name='refresh_repos')
            refresh_latest_commits.delay = MagicMock(name='refresh_commits')

            authorize_user({'login': 'offline', 'gravatar_id': '',
                            'email': ''}, token='')

            refresh_repositories.delay.assert_called_once_with('offline', '')

    def test_execute_refresh_latest_commit_after_login(self):
        with app.test_request_context('/'):
            refresh_repositories.delay = MagicMock(name='refresh_repos')
            refresh_latest_commits.delay = MagicMock(name='refresh_commits')

            authorize_user({'login': 'offline', 'gravatar_id': '',
                            'email': ''}, token='')

            refresh_latest_commits.delay.assert_called_once_with()
