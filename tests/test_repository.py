import unittest

from mock import MagicMock

from bakery.app import app
from bakery.gitauth.views import authorize_user
from bakery.tasks import refresh_repositories, refresh_latest_commits


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
