import uuid
from typing import List, Optional
from src.models.order import Order
from src.models.product import Product
from src.models.customer import Customer
from src.inventory.inventory_manager import InventoryManager
from src.notifications.notification_service import NotificationService, CustomerNotificationObserver
from src.shipping.shipping_strategy import ShippingStrategyFactory


class OrderFactory:
    """
    Factory class for creating orders with appropriate initialization and setup.
    """

    @staticmethod
    def create_order(customer: Customer, products: List[tuple[Product, int]], shipping_type: str, shipping_address: str) -> Optional[Order]:
        """
        Create a new order with the specified products and shipping details.
        Returns None if the order cannot be created (e.g., insufficient stock).
        """
        # Create a new order with a unique ID
        order_id = str(uuid.uuid4())
        order = Order(id=order_id, customer_id=customer.id)
        order.shipping_address = shipping_address

        # Get inventory manager instance
        inventory_manager = InventoryManager()

        # Try to add all products to the order
        for product, quantity in products:
            if not order.add_item(product, quantity):
                return None  # Order creation failed due to insufficient stock

        # Set up shipping strategy
        try:
            shipping_strategy = ShippingStrategyFactory.get_strategy(shipping_type)
            order.set_shipping_strategy(shipping_strategy)
            order.calculate_shipping_cost()  # Burada artık parametre yok
        except (ValueError, Exception) as e:
            print(f"Error setting up shipping: {e}")
            return None

        # Update inventory
        for item in order.items:
            inventory_manager.update_stock(item.product.id, -item.quantity)

        # Set up notification observer for the customer
        notification_service = NotificationService()
        observer = CustomerNotificationObserver(customer)
        notification_service.attach("order_status", observer)

        # Send initial notification
        notification_service.notify(
            "order_status",
            f"Order {order_id} has been created successfully"
        )

        # Add order to customer's history
        customer.add_order(order)

        return order
