from bakery import create_app
from bakery.app import db

app = create_app(app_name='bakery')
app.config['DEBUG'] = True
app.config.from_object('config')
app.config.from_pyfile('local.cfg', silent=True)

ctx = app.test_request_context('/')
ctx.push()
print(db)
db.drop_all()
db.create_all()
ctx.pop()
