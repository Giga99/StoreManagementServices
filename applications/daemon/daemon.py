import threading
from time import sleep

from flask import Flask
from redis import Redis
from sqlalchemy_utils import database_exists, create_database

from applications.configuration import Configuration
from applications.models import database, Product, Category, ProductCategory, Order, ProductOrder

application = Flask(__name__)
application.config.from_object(Configuration)


def daemonWork():
    with application.app_context() as context:
        while True:
            with Redis(host=Configuration.REDIS_HOST) as redis:
                row = redis.blpop(Configuration.REDIS_PRODUCTS_LIST)[1].decode("utf-8")
                data = row.split(",")
                categories = data[0].split("|")
                name = data[1]
                quantity = int(data[2])
                price = float(data[3])

                product = Product.query.filter(Product.name == name).first()

                if not product:
                    product = Product(name=name, quantity=quantity, price=price)
                    database.session.add(product)
                    database.session.commit()

                    for category_name in categories:
                        category = Category.query.filter(Category.name == category_name).first()

                        if not category:
                            category = Category(name=category_name, numberOfSoldProducts=0)
                            database.session.add(category)
                            database.session.commit()

                        product_category = ProductCategory(productId=product.id, categoryId=category.id)
                        database.session.add(product_category)
                        database.session.commit()
                else:
                    categories_for_product = [category.name for category in product.categories]

                    bad_categories = False
                    for category_name in categories:
                        if category_name not in categories_for_product:
                            print("This category({}) isn't category for product!".format(category_name))
                            bad_categories = True
                            break
                    if bad_categories:
                        continue

                    database.session.query(Product).filter(Product.id == product.id).update(
                        {'price': (Product.quantity * Product.price + quantity * price) / (Product.quantity + quantity)}
                    )
                    database.session.query(Product).filter(Product.id == product.id).update(
                        {'quantity': Product.quantity + quantity}
                    )
                    database.session.commit()

                    pending_product_orders = product.get_pending_product_orders()
                    for product_order in pending_product_orders:
                        if (product_order.requested - product_order.received) <= product.quantity:
                            database.session.query(Product).filter(Product.id == product.id).update(
                                {'quantity': Product.quantity - (product_order.requested - product_order.received)}
                            )
                            database.session.query(ProductOrder).filter(ProductOrder.id == product_order.id).update(
                                {'received': product_order.requested}
                            )
                            database.session.commit()
                        else:
                            database.session.query(Product).filter(Product.id == product.id).update({'quantity': 0})
                            database.session.query(ProductOrder).filter(ProductOrder.id == product_order.id).update(
                                {'received': ProductOrder.received + product.quantity}
                            )
                            database.session.commit()
                            break


if __name__ == "__main__":
    done = False
    initRequired = True
    while not done:
        try:
            if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
                create_database(application.config["SQLALCHEMY_DATABASE_URI"])
            else:
                initRequired = False

            done = True
        except Exception as ex:
            print("Database didn't respond. Try again in 1 sec.")
            sleep(1)

    database.init_app(application)

    if initRequired:
        with application.app_context() as context:
            database.create_all()
            database.session.commit()

    daemonThread = threading.Thread(name="daemon_product_thread", target=daemonWork, daemon=True)
    daemonThread.start()

    # application.run(debug=True, host="0.0.0.0", port=5001)
    application.run(debug=False, port=5005)
    daemonThread.join()
