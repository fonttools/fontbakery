from bakery import create_app

app = create_app(app_name='bakery')
app.config['DEBUG'] = True
app.config.from_object('config')
app.config.from_pyfile('local.cfg', silent=True)

def make_celery(_app):
    _celery = Celery(_app.import_name, broker=_app.config['CELERY_BROKER_URL'])
    _celery.conf.update(_app.config)
    TaskBase = _celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    _celery.Task = ContextTask
    return _celery

# Celery.
from celery import Celery
celery = make_celery(app)
import ipdb; ipdb.set_trace()