from typing import Dict, Optional
from decimal import Decimal
from src.models.product import Product
from src.data.storage import JsonStorage

class InventoryManager:

    """
       Ürün envanterini yöneten Singleton sınıf.
       Ürün ekleme, silme, stok güncelleme gibi işlemleri içerir.
       """

    _instance = None # Singleton için tek bir örnek saklanır.

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._products: Dict[str, Product] = {}
            self._storage = JsonStorage()
            self._load_products()
            self._initialized = True

    def _load_products(self):

        products_data = self._storage.load_data('products', default={})
        for product_data in products_data.values():
            product = Product(
                id=product_data['id'],
                name=product_data['name'],
                description=product_data['description'],
                price=Decimal(product_data['price']),
                category=product_data['category'],
                stock_quantity=product_data['stock_quantity']
            )
            self._products[product.id] = product

    def add_product(self, product: Product) -> None:

        self._products[product.id] = product
        self._save_products()

    def remove_product(self, product_id: str) -> None:

        if product_id in self._products:
            del self._products[product_id]
            self._save_products()

    def get_product(self, product_id: str) -> Optional[Product]:
        #ID'sine göre bir ürünü döner. Bulamazsa None döner.
        return self._products.get(product_id)

    def update_stock(self, product_id: str, quantity_change: int) -> bool:

        product = self.get_product(product_id)
        if not product:
            return False

        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            return False

        product.stock_quantity = new_quantity
        self._save_products()
        return True

    def get_all_products(self) -> Dict[str, Product]:
        return self._products.copy()

    def get_products_by_category(self, category: str) -> Dict[str, Product]:
        return {
            pid: product
            for pid, product in self._products.items()
            if product.category == category
        }

    def _save_products(self):

        products_data = {
            p.id: {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': str(p.price),
                'category': p.category,
                'stock_quantity': p.stock_quantity
            }
            for p in self._products.values()
        }
        self._storage.save_data('products', products_data)