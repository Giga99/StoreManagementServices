from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from sqlalchemy import desc, func

from applications.decorators import roleCheck
from applications.models import database, Product, Category, ProductOrder
from configuration import Configuration

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="admin")
def getProductStatistics():
    statistics = [
        {
            "name": product_order[0],
            "sold": int(product_order[1]),
            "waiting": int(product_order[2])
        } for product_order in ProductOrder.query.join(Product).with_entities(
            Product.name,
            func.sum(ProductOrder.requested),
            func.sum(ProductOrder.requested - ProductOrder.received)
        ).group_by(Product.name).all()
    ]

    return jsonify(statistics=statistics)


@application.route("/categoryStatistics", methods=["GET"])
@roleCheck(role="admin")
def getCategoryStatistics():
    categories = Category.query.order_by(desc(Category.numberOfSoldProducts), Category.name).all()
    statistics = [c.name for c in categories]

    return jsonify(statistics=statistics)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
