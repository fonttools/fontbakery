from ..extensions import db

# from ..tasks import (add_logger, git_clone, process_project, project_state_get,
#     project_state_save, project_state_push, remove_logger, read_tree, read_license,
#     read_metadata, save_metadata, read_description, save_description, read_log, read_yaml,
#     project_tests)

class Project(db.Model):
    __tablename__ = 'project'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    name = db.Column(db.String(60), index=True)
    full_name = db.Column(db.String(60))
    html_url = db.Column(db.String(60))
    data = db.Column(db.PickleType())
    clone = db.Column(db.String(400))
    is_github = db.Column(db.Boolean(), index=True)

    builds = db.relationship('ProjectBuild', backref='project', lazy='dynamic')

    state = None



    def cache_update(self, data):
        self.html_url = data['html_url']
        self.name = data['name']
        self.data = data

    # def get_state(self, full = False):
    #     if not self.state:
    #         self.state = project_state_get(login = self.login, project_id = self.id, full = full)


class ProjectBuild(db.Model):
    __tablename__ = 'project_build'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    githash = db.Column(db.String(40))
    is_success = db.Column(db.Boolean())
