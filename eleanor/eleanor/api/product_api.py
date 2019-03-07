#!/usr/bin/env python
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from eleanor.db import db
from eleanor.db.models.products import ProductModel
from eleanor.utils.api_utils import json_response


product_api = Blueprint('product_api', __name__)
api = Api(product_api, catch_all_404s=True)


class Product(Resource):
    method_decorators = [
        json_response
    ]

    """
    Example:
        POST: initiating the user registration.
            curl -i -X POST -H "Content-Type: application/json" -d
            '{
                "product_name": "TV",
                "product_type": "consumer good",
                "price": "600"
            }'
            http://localhost/api/products
    """

    def post(self):
        product_name = request.json.get('product_name')
        product_type = request.json.get('product_type')
        price = request.json.get('price')

        current_app.logger.info(
            "New Product {0} registered".format(product_name))

        product_data = dict(
            product_name=product_name,
            product_type=product_type,
            price=price
        )

        product = ProductModel(
            product_name=product_data["product_name"],
            product_type=product_data["product_type"],
            price=product_data["price"],
        )
        product_id = product.id

        db.session.add(product)
        print("hello")
        db.session.commit()

        return {
            "status": "success",
            "product_id": product_id
        }
        # return {
        #     "status": "success",
        #     "product_id": product.id
        # }

    def get(self, product_id):
        product = ProductModel.query.get(product_id)
        return product.to_json()


api.add_resource(
    Product,
    '/product',
    '/product/<string:product_id>'

)
