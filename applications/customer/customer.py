import http

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity

from applications.models import database
from configuration import Configuration
from customer_controller import CustomerController
from commons.decorators import roleCheck
from commons.exceptions import BadRequestException

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

customer_controller = CustomerController()


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
def search_product():
    name = request.args["name"] if "name" in request.args.keys() else ""
    category = request.args["category"] if "category" in request.args.keys() else ""

    categories, products = customer_controller.search_product(name, category)

    return jsonify(categories=categories, products=products), http.HTTPStatus.OK


@application.route("/order", methods=["POST"])
@roleCheck(role="customer")
def order_products():
    requests: list = request.json.get("requests", None)
    identity = get_jwt_identity()

    if requests is None:
        return jsonify(message="Field requests is missing."), http.HTTPStatus.BAD_REQUEST

    if len(requests) == 0:
        return jsonify(message="Field requests is empty."), http.HTTPStatus.BAD_REQUEST

    result = None
    try:
        result = customer_controller.order_products(identity, requests)
    except BadRequestException as ex:
        return jsonify(message=str(ex)), http.HTTPStatus.BAD_REQUEST

    return jsonify(id=result), http.HTTPStatus.OK


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
def get_orders():
    identity = get_jwt_identity()

    orders = [
        {
            "products": [product_order.to_dict() for product_order in order.get_product_orders()],
            "price": sum(product_order.requested * product_order.price for product_order in order.get_product_orders()),
            "status": order.status.name,
            "timestamp": order.timestamp.isoformat()
        } for order in customer_controller.get_orders(identity)
    ]

    return jsonify(orders=orders), http.HTTPStatus.OK


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
