from __future__ import absolute_import
from eleanor.eleanor import create_app
from eleanor.celery.extensions import set_celery


flask_app = create_app()
celery = set_celery(flask_app)

if __name__ == '__main__':
    with flask_app.app_context():
        celery.start()

# celery -A start_celery worker -l debug -P gevent
