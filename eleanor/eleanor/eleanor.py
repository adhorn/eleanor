from __future__ import absolute_import
from gevent.monkey import patch_all, patch_time
patch_all()
patch_time()
from flask import Flask
from eleanor.db import db
from eleanor.utils.util import configure_logging
from eleanor.api.task_api import task_api
from eleanor.api.users_api import users_auth_api
from eleanor.default_settings import URL_PREFIX_VERSION
from eleanor.celery.extensions import celery


def create_app(config_module=None):
    app = Flask(__name__)
    app.config.from_object('eleanor.default_settings')
    if config_module:
        app.config.from_object(config_module)
    app.config.from_envvar('ELEANOR_SETTINGS', silent=True)
    configure_logging(app)
    db.init_app(app)
    with app.app_context():
        app.logger.debug("Initializing the Database")
        db.engine.pool._use_threadlocal = True
    app.register_blueprint(task_api, url_prefix=URL_PREFIX_VERSION)
    app.register_blueprint(users_auth_api, url_prefix=URL_PREFIX_VERSION)
    app.logger.info("Flask App Ready To Go")
    celery.config_from_object(app.config)
    return app


app = create_app()

HOST = app.config['HOST']
PORT = app.config['PORT']

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)

# celery -A run_celery worker -l debug -P gevent
# gunicorn -w 1 -b 0.0.0.0:5555 -k gevent eleanor.eleanor:app --reload
