from sqlalchemy import func, desc

from applications.models import Product, ProductOrder, Category


class AdminController:

    def get_products_statistics(self):
        return ProductOrder.query.join(Product).with_entities(
            Product.name,
            func.sum(ProductOrder.requested),
            func.sum(ProductOrder.requested - ProductOrder.received)
        ).group_by(Product.name).all()

    def get_category_statistics(self):
        return Category.query.order_by(desc(Category.numberOfSoldProducts), Category.name).all()
