
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from datetime import date

# Abstract base class

class FinancialEntry(ABC):

    def __init__(self, amount: float, description: str, entry_date: date) -> None:
        self._id: str = str(uuid.uuid4())
        self.amount = amount          # uses setter for validation
        self._description: str = description
        self._date: date = entry_date

    @property
    @abstractmethod
    def entry_type(self) -> str:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Amount must be a number.")
        if value <= 0:
            raise ValueError("Amount must be a positive number.")
        self._amount = float(value)

    # -- read-only properties -------------------------------------------
    @property
    def id(self) -> str:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @property
    def date(self) -> date:
        return self._date

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(id={self._id[:8]}…, "
                f"amount={self._amount:.2f}, date={self._date})")

