from flask import current_app
from eleanor.celery.extensions import celery as ce
from celery.result import AsyncResult
from celery.task.control import ping
import random
import sys
import traceback


@ce.task(bind=True)
def add(self, x, y):
    try:
        current_app.logger.debug(
            "Task: Test with {0} and {1} ".format(x, y))
        return x + y

    except Exception as exc:
            raise self.retry(exc=exc)


@ce.task(bind=True, default_retry_delay=1)
def add_retry(self, x, y):
    try:
        1 / random.randrange(0)
        current_app.logger.debug(
            "Task: Test with {0} and {1} ".format(x, y))
        return x + y

    except Exception as exc:
            raise self.retry(exc=exc, max_retries=10)


@ce.task(bind=True)
def add_expo(self, x, y):
    try:
        1 / random.randrange(0)
        current_app.logger.debug(
            "Task: Test with {0} and {1} ".format(x, y))
        return x + y
    except Exception as exc:
        self.retry(
            exc=exc,
            max_retries=5,
            countdown=int(
                random.uniform(2, 4) ** self.request.retries)
        )


def get_task(task_id):
    r = AsyncResult(task_id, app=ce)
    return r.state, str(r.result)


def get_ping():
    r = ping(app=ce)
    current_app.logger.debug("Ping {0} ".format(r))
    return r
