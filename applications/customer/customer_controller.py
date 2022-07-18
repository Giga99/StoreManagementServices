from sqlalchemy import and_

from applications.models import database, Product, Category, ProductCategory, Order, ProductOrder
from commons.exceptions import BadRequestException


class CustomerController:

    def search_product(self, name, category):
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
        return categories, products

    def order_products(self, identity, requests):
        try:
            order = Order(userEmail=identity, statusId=2)
            database.session.add(order)
            database.session.flush()

            index = 0
            for req in requests:
                product_id = req.get("id", None)
                requested_quantity = req.get("quantity", None)

                if product_id is None:
                    raise BadRequestException("Product id is missing for request number {}.".format(index))

                if requested_quantity is None:
                    raise BadRequestException("Product quantity is missing for request number {}.".format(index))

                if type(product_id) is not int or product_id < 0:
                    raise BadRequestException("Invalid product id for request number {}.".format(index))

                if type(requested_quantity) is not int or requested_quantity < 1:
                    raise BadRequestException("Invalid product quantity for request number {}.".format(index))

                product = Product.query.filter(Product.id == product_id).first()
                if not product:
                    raise BadRequestException("Invalid product for request number {}.".format(index))

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
        except:
            database.session.rollback()
            raise
        else:
            database.session.commit()

        return order.id

    def get_orders(self, identity):
        return Order.query.filter(Order.userEmail == identity).all()
