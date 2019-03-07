#!/usr/bin/env python
from datetime import datetime
from eleanor.db import db
from eleanor.utils.util import generate_uuid


class ProductModel(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.VARCHAR(255), primary_key=True)
    timestamp = db.Column(db.DateTime, index=True)
    product_name = db.Column(db.String(120), index=True, unique=True)
    product_type = db.Column(db.String(120), index=True)
    price = db.Column(db.String(120))

    def __init__(self, **kwargs):
        self.id = generate_uuid()
        self.timestamp = datetime.utcnow()
        super(ProductModel, self).__init__(**kwargs)

    def __repr__(self):
        return '<Product {}>'.format(self.product_name)

    def to_json(self):
        json_product = {
            'product_name': self.product_name,
            'product_type': self.product_type,
            'price': self.price,
            'id': self.id,
            'timestamp': self.timestamp
        }
        return json_product
