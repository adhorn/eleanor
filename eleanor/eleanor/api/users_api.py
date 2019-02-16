#!/usr/bin/env python
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from eleanor.db import db
from eleanor.db.models.users import UserModel
from eleanor.utils.api_utils import json_response
from eleanor.utils.util import generate_uuid


users_auth_api = Blueprint('users_auth_api', __name__)
api = Api(users_auth_api, catch_all_404s=True)


class User(Resource):
    method_decorators = [
        json_response
    ]

    """
    Example:
        POST: initiating the user registration.
            curl -i -X POST -H "Content-Type: application/json" -d
            '{
                "username": "user",
                "password": "password",
                "phone": "+358456121314"
            }'
            http://localhost/api/v1.0/user?key=foobar123
    """

    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        phone = request.json.get('phone')

        current_app.logger.info(
            "New User {0} registered".format(phone))

        userdata = dict(
            username=username,
            password=password,
            phone=phone,
            id=generate_uuid()
        )

        user = UserModel(
            username=userdata["username"],
            phone=userdata["phone"],
            id=userdata["id"]
        )
        user.hash_password(userdata["password"])

        db.session.add(user)
        db.session.commit()

        return {
            "status": "success",
            "client_id": userdata["id"]
        }
        # return {
        #     "status": "success",
        #     "client_id": user.id
        # }


api.add_resource(
    User,
    '/user'
)
