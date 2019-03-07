import socket
from flask import Blueprint, current_app
from flask_restful import Api, Resource
from eleanor.utils.api_utils import json_response, api_error_response
from eleanor.celery import tasks
from eleanor.db import db
from eleanor.utils.redis import ping

try:
    from eleanor.settings import DEBUG
except ImportError:
    from eleanor.default_settings import DEBUG


echo_api = Blueprint('echo_api', __name__)
api = Api(echo_api, catch_all_404s=True)


class Echo(Resource):
    method_decorators = [
        json_response
    ]

    def get(self):
        current_app.logger.info("Calling Echo")
        return {
            "Status": "Up and running!"
        }


class HealthCheck(Resource):
    method_decorators = [
        json_response,
        # ratelimit(limit=60, per=60)
    ]

    def get(self):
        try:
            hostname = (
                [(
                    s.connect(('8.8.8.8', 80)),
                    s.getsockname()[0],
                    s.close()) for s in [
                        socket.socket(
                            socket.AF_INET,
                            socket.SOCK_DGRAM)]][0][1])
        except Exception as e:
            current_app.logger.warning(
                "Exception: Connecting to the outside world {}".format(str(e)))
            hostname = 'Not Available'

        try:
            database = 'Accessible' if db.engine.dialect.has_table(
                db.engine.connect(), "user") else 'Fails'

        except Exception as e:
            current_app.logger.warning(
                "Exception: Connecting to Database {}".format(str(e)))
            database = 'Fails'

        redis = None
        try:
            redis = 'Accessible' if ping() is not None else 'Fails'
        except Exception as e:
            current_app.logger.warning(
                "Exception: Connecting to Redis {}".format(str(e)))
            redis = 'Fails'

        try:
            test_task = tasks.add.delay(4, 4)
            tasks_test = 'Accessible' if test_task.get(
                timeout=4) is 8 else 'Fails'
        except Exception as e:
            current_app.logger.warning(
                "Exception: Connecting to Celery failed {}".format(str(e)))
            tasks_test = 'Fails'

        response = {
            "App Status": "Accessible",
            "DB Status": database,
            "App Hostname": hostname,
            "Celery Workers": tasks_test,
            "Redis": redis
        }

        if 'Fails' in response.values():
            return api_error_response(
                code=503,
                errors=response,
                message='Downstream service down')
        else:
            return response


class Sha(Resource):
    """
    Get the commit number and author
    of the code running in the current application

    Example:
        http GET http://localhost/api/sha

    """
    method_decorators = [
        json_response,
    ]

    def get(self):
        with open('.git/refs/heads/master') as f:
                return {
                    'sha_commit': f.read()
                }


api.add_resource(Echo, '/echo')
api.add_resource(HealthCheck, '/health')
api.add_resource(Sha, '/sha')
api.add_resource(Resource, '/resource')
