from flask import Blueprint, current_app, make_response
from flask_restful import Api, Resource
from eleanor.utils.api_utils import json_response
from eleanor.celery import tasks
from eleanor.db import db
from eleanor.utils.redis import ping, set_key
from eleanor.utils.healthcheck import HealthCheck
from eleanor.db.models.products import ProductModel
import json


echo_api = Blueprint('echo_api', __name__)
api = Api(echo_api, catch_all_404s=True)


class Echo(Resource):
    method_decorators = [
        json_response
    ]

    def get(self):
        # current_app.logger.info("Calling Echo")
        return {
            "Status": "Up and running..."
        }


def db_master_check():
    db.session.using_bind("master").query(ProductModel).all()
    return True, "db master ok"


def db_slave_check():
    db.session.using_bind("slave").query(ProductModel).all()
    return True, "db slave ok"


def redis_check():
    ping()
    return True, "redis ok"


def task_check():
    test_task = tasks.add.delay(4, 4)
    test_task.get(timeout=4)
    return True, "tasks ok"


health = HealthCheck(
    checkers=[
        db_master_check,
        db_slave_check,
        redis_check,
        task_check
    ]
)


class HealthCheck(Resource):

    def get(self):
        message, status = health.check()

        check_force = [
            mess for mess in message['results']
            if mess["checker"] == 'db_slave_check' and
            'OperationalError' in str(mess["output"])
        ]
        if check_force:
            set_key('MASTER', 'FORCE')
            current_app.logger.debug("set FORCE MASTER")
        else:
            set_key('MASTER', 'NO FORCE')
            current_app.logger.debug("NO set FORCE MASTER")

        headers = [('Retry-After', '30')]
        return make_response(json.dumps(message), status, headers)


api.add_resource(Echo, '/echo')

api.add_resource(HealthCheck, '/health')
