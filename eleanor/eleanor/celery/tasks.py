from flask import current_app
from eleanor.celery.extensions import celery as ce
from celery.result import AsyncResult
import random


@ce.task(bind=True)
def add(self, x, y):
    try:
        1 / random.randrange(2)
        current_app.logger.debug(
            "Task: Test with {0} and {1} ".format(x, y))
        # return x + y
    except Exception as exc:
        self.retry(
            exc=exc,
            max_retries=5,
            countdown=int(
                random.uniform(2, 4) ** self.request.retries)
        )


def get_task(task_id):
    return AsyncResult(task_id, app=ce).state
