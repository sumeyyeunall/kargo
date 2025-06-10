from typing import List
from datetime import datetime
from src.models.order import Order


class Customer:
    """
    Represents a customer in the e-commerce system.
    """

    def __init__(self, id: str, name: str, email: str, address: str, phone: str):
        self.id = id
        self.name = name
        self.email = email
        self.address = address
        self.phone = phone
        self.order_history: List['Order'] = []
        self.registration_date = datetime.now()

    def add_order(self, order: 'Order') -> None:
        """Add an order to the customer's order history."""
        self.order_history.append(order)

    def get_order_history(self) -> List['Order']:
        """Get the customer's order history."""
        return self.order_history
