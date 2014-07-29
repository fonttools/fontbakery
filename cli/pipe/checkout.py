from git import Repo


class Checkout(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.bakery = bakery

    def execute(self, pipedata, prefix=''):
        revision = pipedata.get('commit') or 'master'

        repo = Repo(self.project_root)
        headcommit = repo.git.rev_parse('HEAD', short=True)
        if revision != 'master':
            msg = 'Checkout commit %s\n' % headcommit
        else:
            msg = 'Checkout most recent commit (%s)' % headcommit

        task = self.bakery.logging_task(msg)

        if self.bakery.forcerun:
            return

        self.bakery.logging_cmd('git checkout %s' % revision)
        try:
            repo.git.checkout(revision)
        except:
            self.bakery.logging_task_done(task, failed=True)
            raise

        self.bakery.logging_task_done(task)
