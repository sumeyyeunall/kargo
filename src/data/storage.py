import json
import os
from typing import Dict, Any, Optional

class JsonStorage:
    """
    Uygulama için JSON tabanlı veri saklama sınıfı.
    Kullanıcı ve admin verilerini JSON dosyalarında tutar.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_directory()
        self._ensure_admin_account()

    def _ensure_data_directory(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self.data_dir, f"{filename}.json")

    def _ensure_admin_account(self):
        admins = self.load_data("admins", default={})
        if not admins:
            admins["admin@example.com"] = {
                "email": "admin@example.com",
                "password": "123"
            }
            self.save_data("admins", admins)

    def save_data(self, filename: str, data: Any):
        path = self._get_file_path(filename)
        with open(path, "w") as file:
            json.dump(data, file, indent=2)

    def load_data(self, filename: str, default: Any = None) -> Any:
        path = self._get_file_path(filename)
        if not os.path.exists(path):
            return default
        with open(path, "r") as file:
            return json.load(file)

    def register_customer(self, id, name, email, password, address, phone):
        customers = self.load_data('customers', default={})

        #Aynı e-posta daha önce kayıtlı mı kontrol et
        for customer_id, customer in customers.items():
            if customer['email'] == email:
                return False

        # Yeni musteri verisi ekle
        customers[id] = {
            'id': id,
            'name': name,
            'email': email,
            'password': password,
            'address': address,
            'phone': phone
        }

        self.save_data('customers', customers)
        return True

    def authenticate_customer(self, email, password):
        customers = self.load_data('customers', default={})

        for customer_id, customer_data in customers.items():
            if (
                    isinstance(customer_data, dict) and
                    customer_data.get('email') == email and
                    customer_data.get('password') == password
            ):
                return customer_data

        return None  #Kimlik doğrulama başarısız
    def authenticate_admin(self, email: str, password: str) -> bool:
        admins = self.load_data("admins", default={})
        admin = admins.get(email)
        return admin and admin["password"] == password
