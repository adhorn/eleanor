#!/usr/bin/env python
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from datetime import datetime
from flask import current_app
from eleanor.db import db
from eleanor.utils.util import generate_uuid
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)


class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.VARCHAR(255), primary_key=True)
    timestamp = db.Column(db.DateTime, index=True)
    phone = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, **kwargs):
        self.id = generate_uuid()
        self.timestamp = datetime.utcnow()
        super(UserModel, self).__init__(**kwargs)

    def __repr__(self):
        return '<Username {}>'.format(self.username)

    def hash_password(self, password):
        #  The custom_app_context object is an
        #  based on the sha256_crypt hashing algorithm.
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):  # 600 seconds = 10 minutes
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def to_json(self):
        json_user = {
            'username': self.username,
            'phone': self.phone,
            'id': self.id,
            'last modified': self.timestamp
        }
        return json_user

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = UserModel.query.get(data['id'])
        return user
