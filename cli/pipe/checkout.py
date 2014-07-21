from git import Repo
from cli.system import stdoutlog


class Checkout(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata, prefix=''):
        repo = Repo(self.project_root)
        revision = pipedata.get('commit') or 'master'
        headcommit = repo.git.rev_parse('HEAD', short=True)
        if revision != 'master':
            msg = 'Checkout commit %s\n' % headcommit
        else:
            msg = 'Checkout most recent commit (%s)' % headcommit
        self.stdout_pipe.write(msg, prefix='### %s ' % prefix)
        repo.git.checkout(revision)
