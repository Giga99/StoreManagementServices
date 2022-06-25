from dataclasses import dataclass


@dataclass
class ProductOrderRequest:
    product_id: int
    product_quantity: int
    product_price: float
    can_buy_product: bool
