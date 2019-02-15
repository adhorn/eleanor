import os
basedir = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.1'
URL_PREFIX_VERSION = '/api'
SECRET_KEY = '\x1d\xf9\x92\xd7|$\xd3\xe6*\xf3\xb3\x05\x1c\xd0\xc82\xcePh\x04\x97Gj\x9d'

HOST = 'localhost'
PORT = 5555
DEBUG = True
BRANCH = 'master'

TRAP_HTTP_EXCEPTIONS = True
TRAP_BAD_REQUEST_ERRORS = True
JSONIFY_PRETTYPRINT_REGULAR = True

ERROR_404_HELP = False

ERROR_TO_FILE = True
ERROR_LOG_NAME = 'logs/errors.log'


CELERY_BROKER_URL = ['redis://redis:6379/0']
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERYD_LOG_FILE = "logs/celery.log"
CELERY_IGNORE_RESULT = False
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_ENABLE_UTC = True
CELERY_DEFAULT_ROUTING_KEY = "eleanor"
CELERY_DEFAULT_QUEUE = 'eleanor'
CELERY_DEFAULT_EXCHANGE = "eleanor"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True}
BROKER_CONNECTION_MAX_RETRIES = 0
BROKER_FAILOVER_STRATEGY = "round-robin"
BROKER_HEARTBEAT = 10

SQLALCHEMY_DATABASE_URI = 'mysql://eleanordbuser:foobar123@mysql/eleanordb'

SQLALCHEMY_BINDS = {
    'master': 'mysql://eleanordbuser:foobar123@mysql/eleanordb',
    'slave': 'mysql://eleanordbuser:foobar123@mysql/eleanordb'
}

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_RECORD_QUERIES = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.4
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 20


DROP_BEFORE_CREATE = True