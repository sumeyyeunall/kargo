from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

class ShippingStrategy(ABC):

    @abstractmethod
    def calculate_cost(self) -> Decimal:
        pass

    @abstractmethod
    def get_estimated_days(self) -> int: #delivery time in days
        pass

class FastShipping(ShippingStrategy):

    def calculate_cost(self) -> Decimal:
        return Decimal('50.00')
    def get_estimated_days(self) -> int:
        return 2

class EconomicShipping(ShippingStrategy):

    def calculate_cost(self) -> Decimal:
        return Decimal('10.00')  # Sabit ücret

    def get_estimated_days(self) -> int:
        return 5

class DroneShipping(ShippingStrategy):

    def calculate_cost(self) -> Decimal:
        return Decimal('100.00')

    def get_estimated_days(self) -> int:
        return 1

class ShippingStrategyFactory:  #factory for strategy instances

    _strategies: Dict[str, type] = {
        'fast': FastShipping,
        'economic': EconomicShipping,
        'drone': DroneShipping
    }

    @classmethod
    def get_strategy(cls, strategy_type: str) -> ShippingStrategy:
        strategy_class = cls._strategies.get(strategy_type.lower())
        if not strategy_class:
            raise ValueError(f"Unknown shipping strategy: {strategy_type}")
        return strategy_class()