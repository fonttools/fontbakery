import unittest

from mock import MagicMock
from bakery.gitauth.views import authorize_user
from bakery.tasks import refresh_repositories


class TestRepository(unittest.TestCase):

    def test_execute_refresh_repos_task_after_login(self):
        refresh_repositories.delay = MagicMock(name='refresh_repos')

        authorize_user({'login': 'offline', 'gravatar_id': '',
                        'email': ''}, token='')

        refresh_repositories.delay.assert_called_once_with('offline', '')
