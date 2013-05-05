from datetime import datetime
from ..extensions import db

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(60), index=True)
    payload = db.Column(db.PickleType())
    status = db.Column(db.Integer(), default=0, index=True) # 0 - open, 1 - process, 2 - closed
    created = db.Column(db.DateTime(), default=datetime.now)