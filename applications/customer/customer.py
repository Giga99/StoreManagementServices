from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity
from sqlalchemy import and_

from applications.configuration import Configuration
from applications.decorators import roleCheck
from applications.models import database, Product, Category, ProductCategory, Order, ProductOrder
from applications.utils import ProductOrderRequest

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
def searchProduct():
    name = request.args["name"] if "name" in request.args.keys() else ""
    category = request.args["category"] if "category" in request.args.keys() else ""

    categories = [c.name for c in Category.query.join(ProductCategory).join(Product).filter(
        and_(
            Category.name.like(f"%{category}%"),
            Product.name.like(f"%{name}%")
        )
    ).all()]

    products = [
        {
            "categories": [c.name for c in p.categories],
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "quantity": p.quantity
        } for p in Product.query.filter(
            and_(
                Product.name.like(f"%{name}%"),
                Category.name.like(f"%{category}%")
            )
        ).all()
    ]

    return jsonify(categories=categories, products=products)


@application.route("/order", methods=["POST"])
@roleCheck(role="customer")
def orderProducts():
    requests: list = request.json.get("requests", None)

    if requests is None:
        return jsonify(message="Field requests is missing."), 400

    if len(requests) == 0:
        return jsonify(message="Field requests is empty."), 400

    product_order_requests: list[ProductOrderRequest] = []
    index = 0
    for req in requests:
        product_id = req.get("id", None)
        product_quantity = req.get("quantity", None)

        if product_id is None:
            return jsonify(message="Product id is missing for request number {}.".format(index)), 400

        if product_quantity is None:
            return jsonify(message="Product quantity is missing for request number {}.".format(index)), 400

        if type(product_id) is not int or product_id < 0:
            return jsonify(message="Invalid product id for request number {}.".format(index)), 400

        if type(product_quantity) is not int or product_quantity < 1:
            return jsonify(message="Invalid product quantity for request number {}.".format(index)), 400

        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify(message="Invalid product for request number {}.".format(index)), 400

        product_order_requests.append(
            ProductOrderRequest(product_id, product_quantity, product.price, product.quantity >= product_quantity))
        index = index + 1

    identity = get_jwt_identity()
    quantities = dict()
    for p in product_order_requests:
        quantities[p.product_id] = [p.product_quantity if p.can_buy_product else 0, p.product_quantity]
    order = Order(
        price=sum(p.product_price * p.product_quantity for p in product_order_requests),
        statusId=1 if any(p.can_buy_product for p in product_order_requests) else 2,
        userEmail=identity,
        quantities=quantities
    )
    database.session.add(order)
    database.session.commit()

    for p in product_order_requests:
        database.session.add(ProductOrder(productId=p.product_id, orderId=order.id))
        if p.can_buy_product:
            database.session.query(Product).filter(Product.id == p.product_id) \
                .update({'quantity': Product.quantity - p.product_quantity})

    database.session.commit()

    return jsonify(id=order.id)


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
def getOrders():
    identity = get_jwt_identity()

    orders = [
        {
            "products": [
                {
                    "categories": [category.name for category in product.categories],
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "received": order.quantities.get(str(product.id))[0],
                    "requested": order.quantities.get(str(product.id))[1]
                } for product in order.products
            ],
            "price": order.price,
            "status": order.status.name,
            "timestamp": order.timestamp.isoformat()
        } for order in Order.query.filter(Order.userEmail == identity).all()
    ]

    return jsonify(orders=orders)


if __name__ == "__main__":
    database.init_app(application)
    # application.run(debug=True, host="0.0.0.0", port=5001)
    application.run(debug=True, port=5001)
