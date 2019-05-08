from flask import Blueprint, current_app
from flask_restful import Api, Resource
from eleanor.utils.api_utils import json_response
from eleanor.celery import tasks


task_api = Blueprint('task_api', __name__)
api = Api(task_api, catch_all_404s=True)


class Echo(Resource):
    method_decorators = [
        json_response
    ]

    def get(self):
        current_app.logger.info("Calling Echo")
        return {
            "Status": "Up and running!"
        }


class AddTask(Resource):
    method_decorators = [
        json_response
    ]

    def put(self):
        current_app.logger.info("Calling Add")

        Task_ID = tasks.add.apply_async(
            [10, 30],
        )

        return {
            "Task ID": Task_ID.task_id
        }

    def get(self, task_id):
        current_app.logger.info("Calling Get Task ID")

        return {
            "{}".format(task_id): tasks.get_task(task_id)
        }


class AddTaskRetry(Resource):
    method_decorators = [
        json_response
    ]

    def put(self):
        current_app.logger.info("Calling Add")

        Task_ID = tasks.add_retry.apply_async(
            [10, 30],
        )

        return {
            "Task ID": Task_ID.task_id
        }


class AddTaskExpo(Resource):
    method_decorators = [
        json_response
    ]

    def put(self):
        current_app.logger.info("Calling Add")

        Task_ID = tasks.add_expo.apply_async(
            [10, 30],
        )

        return {
            "Task ID": Task_ID.task_id
        }


api.add_resource(
    AddTask,
    '/task',
    '/task/<string:task_id>')


api.add_resource(
    AddTaskRetry,
    '/taskretry')


api.add_resource(
    AddTaskExpo,
    '/taskexpo')

