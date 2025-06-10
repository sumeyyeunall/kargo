from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List
from src.models.product import Product
from src.shipping.shipping_strategy import ShippingStrategy

class OrderStatus(Enum): #order statuses
    CREATED = "created"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem:
    """Represents an item in an order."""
    def __init__(self, product: Product, quantity: int, unit_price: Decimal):
        self.product = product
        self.quantity = quantity
        self.unit_price = unit_price

    @property
    def total_price(self) -> Decimal:
        """Calculate the total price for this order item."""
        return self.unit_price * self.quantity

class Order:
    """Represents an order in the e-commerce system."""
    def __init__(self,id: str,customer_id: str,shipping_address: str = "",shipping_strategy: ShippingStrategy = None):
        self.id = id
        self.customer_id = customer_id
        self.items: List[OrderItem] = []
        self.status = OrderStatus.CREATED
        self.creation_date = datetime.now()
        self.shipping_strategy = shipping_strategy
        self.shipping_address = shipping_address
        self.shipping_cost = Decimal('0')

    @property
    def total_items_price(self) -> Decimal:
        """Calculate the total price of all items in the order."""
        return sum(item.total_price for item in self.items)

    @property
    def total_price(self) -> Decimal:
        """Calculate the total price including shipping."""
        return self.total_items_price + self.shipping_cost

    def add_item(self, product: Product, quantity: int) -> bool:
        """
        Add an item to the order.
        Returns False if the product is not available in sufficient quantity.
        """
        if not product.is_available() or product.stock_quantity < quantity:
            return False

        self.items.append(OrderItem(
            product=product,
            quantity=quantity,
            unit_price=product.price
        ))
        return True

    def set_shipping_strategy(self, strategy: ShippingStrategy) -> None:
        """Set the shipping strategy for this order."""
        self.shipping_strategy = strategy

    def calculate_shipping_cost(self) -> None:
        """Calculate shipping cost based on the selected strategy."""
        if not self.shipping_strategy:
            raise ValueError("Shipping strategy not set")

        self.shipping_cost = self.shipping_strategy.calculate_cost()

    def update_status(self, new_status: OrderStatus) -> None:
        """Update the order status."""
        self.status = new_status
