from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from sqlalchemy import desc

from applications.configuration import Configuration
from applications.decorators import roleCheck
from applications.models import database, Product, Category

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="admin")
def getProductStatistics():
    statistics = [
        {
            "name": product.name,
            "sold": sum(o.quantities[str(product.id)][1] for o in product.orders),
            "waiting": sum(o.quantities[str(product.id)][1] if o.quantities[str(product.id)][0] == 0 else 0 for o in product.orders)
        } for product in Product.query.all()
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
    # application.run(debug=True, host="0.0.0.0", port=5001)
    application.run(debug=True, port=5003)
