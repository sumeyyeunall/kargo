from decimal import Decimal

class Product:
    """
    Represents a product in the e-commerce system.
    """
    def __init__(self, id: str, name: str, description: str,
                 price: Decimal, category: str, stock_quantity: int):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.stock_quantity = stock_quantity

    def is_available(self) -> bool:
        """Check if the product is available in stock."""
        return self.stock_quantity > 0

    def decrease_stock(self, quantity: int) -> bool:
        """
        Decrease the stock quantity by the specified amount.
        Returns True if successful, False if insufficient stock.
        """
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            return True
        return False

    def increase_stock(self, quantity: int) -> None:
        """Increase the stock quantity by the specified amount."""
        self.stock_quantity += quantity
