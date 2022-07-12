from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity
from sqlalchemy import and_

from configuration import Configuration
from applications.decorators import roleCheck
from applications.models import database, Product, Category, ProductCategory, Order, ProductOrder

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
        } for p in Product.query.join(ProductCategory).join(Category).filter(
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

    identity = get_jwt_identity()
    order = Order(userEmail=identity, statusId=2)
    database.session.add(order)
    database.session.flush()

    index = 0
    for req in requests:
        product_id = req.get("id", None)
        requested_quantity = req.get("quantity", None)

        if product_id is None:
            database.session.rollback()
            return jsonify(message="Product id is missing for request number {}.".format(index)), 400

        if requested_quantity is None:
            database.session.rollback()
            return jsonify(message="Product quantity is missing for request number {}.".format(index)), 400

        if type(product_id) is not int or product_id < 0:
            database.session.rollback()
            return jsonify(message="Invalid product id for request number {}.".format(index)), 400

        if type(requested_quantity) is not int or requested_quantity < 1:
            database.session.rollback()
            return jsonify(message="Invalid product quantity for request number {}.".format(index)), 400

        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            database.session.rollback()
            return jsonify(message="Invalid product for request number {}.".format(index)), 400

        received = requested_quantity if requested_quantity <= product.quantity else product.quantity
        product_order = ProductOrder(
            productId=product.id,
            orderId=order.id,
            price=product.price,
            received=received,
            requested=requested_quantity
        )
        database.session.add(product_order)
        database.session.query(Product).filter(Product.id == product.id).update(
            {'quantity': Product.quantity - received}
        )
        for category in product.categories:
            database.session.query(Category).filter(Category.id == category.id).update(
                {'numberOfSoldProducts': Category.numberOfSoldProducts + requested_quantity}
            )
        database.session.flush()
        index = index + 1

    if all(product_order.requested == product_order.received for product_order in order.get_product_orders()):
        database.session.query(Order).filter(Order.id == order.id).update({'statusId': 1})
    database.session.commit()

    return jsonify(id=order.id)


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
def getOrders():
    identity = get_jwt_identity()

    orders = [
        {
            "products": [product_order.to_dict() for product_order in order.get_product_orders()],
            "price": sum(product_order.requested * product_order.price for product_order in order.get_product_orders()),
            "status": order.status.name,
            "timestamp": order.timestamp.isoformat()
        } for order in Order.query.filter(Order.userEmail == identity).all()
    ]

    return jsonify(orders=orders)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
