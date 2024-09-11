from celery import Celery

def make_celery(app):
    print("making celery")
    celery = Celery(
        app.import_name,
        broker=app.config['broker_url'],
        backend=app.config['result_backend'],
    )
    celery.conf.update(
        app.config, 
        task_track_started=True
        )
    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            try:
                with app.app_context():
                    result = self.run(*args, **kwargs)
                    return result
            except Exception as e:
                app.logger.error(f"Task failed: {e}")
                raise
    celery.Task = ContextTask

    return celery
