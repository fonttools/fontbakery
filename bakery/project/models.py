from ..extensions import db

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    name = db.Column(db.String(60), index=True)
    full_name = db.Column(db.String(60))
    html_url = db.Column(db.String(60))
    data = db.Column(db.PickleType())
    clone = db.Column(db.String(400))
    is_github = db.Column(db.Boolean(), index=True)

    def cache_update(self, data):
        self.html_url = data['html_url']
        self.name = data['name']
        self.data = data

# class Ufo(db.Model):
#     __tablename__ = 'project_ufo'
#     id = db.Column(db.Integer, primary_key=True)
#     login = db.Column(db.String(60), index=True)
#     project_id = db.Column(db.Integer())
#     #git_path = db.Column(db.String(200))
#     #ufo_path = db.Column(db.String(200))
#     title = db.Column(db.String(200))
#     # license file link
#     license = db.Column(db.String(200))
