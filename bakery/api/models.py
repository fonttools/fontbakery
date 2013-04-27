from ..extensions import db

class Task(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    name = db.Column(db.String(200))
    avatar = db.Column(db.String(1000))
    email = db.Column(db.String(200))
    github_access_token = db.Column(db.String(200),
        nullable = False, index=True)

    def __init__(self, login):
        self.login = login

    def getAvatar(self, size=24):
        return "https://www.gravatar.com/avatar/%s?s=%d&d=mm" % (self.avatar, size)

    def getGithub(self):
        return "https://github.com/%s" % self.login

    @staticmethod    
    def get_or_init(login):
        user = User.query.filter_by(login=login).first()
        if user is None:
            user = User(login)
        return user
        