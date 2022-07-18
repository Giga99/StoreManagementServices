import http

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from admin_controller import AdminController
from commons.decorators import roleCheck
from applications.models import database
from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

adminController = AdminController()


@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="admin")
def get_product_statistics():
    statistics = [
        {
            "name": product_order[0],
            "sold": int(product_order[1]),
            "waiting": int(product_order[2])
        } for product_order in adminController.get_products_statistics()
    ]

    return jsonify(statistics=statistics), http.HTTPStatus.OK


@application.route("/categoryStatistics", methods=["GET"])
@roleCheck(role="admin")
def get_category_statistics():
    statistics = [c.name for c in adminController.get_category_statistics()]

    return jsonify(statistics=statistics), http.HTTPStatus.OK


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
