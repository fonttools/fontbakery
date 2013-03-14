from .app import celery

@celery.task()
def add_together(a, b):
    return a + b


@celery.task()
def update_user_info():
    pass