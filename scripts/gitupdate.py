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
