# src/notifications/notification_service.py

import logging
from datetime import datetime
from typing import List, Dict
from src.models.customer import Customer
from abc import ABC, abstractmethod

# 🔧 Log dosyası ayarı
logging.basicConfig(
    filename="notifications.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Observer arayüzü
class NotificationObserver(ABC):
    @abstractmethod
    def update(self, message: str) -> None:
        pass

# 🔔 Müşteri bildirimleri için observer
class CustomerNotificationObserver(NotificationObserver):
    def __init__(self, customer: Customer):
        self.customer = customer

    def update(self, message: str) -> None:
        timestamped_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Order Notification for {self.customer.name} ({self.customer.email}): {message}"
        print(timestamped_message)  # Terminale yaz
        logging.info(timestamped_message)  # Log dosyasına yaz

# 🔔 Bildirim servisi (singleton)
class NotificationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._observers: Dict[str, List[NotificationObserver]] = {}
            self._initialized = True

    def attach(self, event_type: str, observer: NotificationObserver) -> None:
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(observer)

    def detach(self, event_type: str, observer: NotificationObserver) -> None:
        if event_type in self._observers:
            self._observers[event_type] = [
                obs for obs in self._observers[event_type] if obs != observer
            ]

    def notify(self, event_type: str, message: str) -> None:
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                observer.update(message)
