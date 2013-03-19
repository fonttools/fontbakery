import datetime
from ..extensions import db

class ProjectCache(db.Model):
    __tablename__ = 'project_cache'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    repos = db.Column(db.Text())
    updated = db.Column(db.DateTime(timezone=False), default=datetime.datetime)

