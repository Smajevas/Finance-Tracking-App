"""
models.py — Core domain models for the Finance Tracker application.

Demonstrates:
- Encapsulation: private attributes with properties/setters
- Abstraction: abstract base class FinancialEntry
- Inheritance: Income and Expense inherit from Transaction
- Polymorphism: describe() and to_dict() overridden in subclasses
"""

from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from datetime import date
from enum import Enum


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class CategoryType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


# ---------------------------------------------------------------------------
# Category  (used via Composition inside Transaction)
# ---------------------------------------------------------------------------

class Category:
    """Represents a named category that belongs to a CategoryType.

    Demonstrates **Encapsulation**: the internal _name and _type are
    private; public access is only through read-only properties.
    """

    def __init__(self, name: str, category_type: CategoryType) -> None:
        self._name: str = self._validate_name(name)
        self._type: CategoryType = category_type

    # -- private helper --------------------------------------------------
    @staticmethod
    def _validate_name(name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Category name cannot be empty.")
        return name

    # -- properties (read-only) ------------------------------------------
    @property
    def name(self) -> str:
        return self._name

    @property
    def category_type(self) -> CategoryType:
        return self._type

    def __repr__(self) -> str:
        return f"Category(name={self._name!r}, type={self._type.value!r})"

    def to_dict(self) -> dict:
        return {"name": self._name, "type": self._type.value}


# ---------------------------------------------------------------------------
# Abstract base class  (Abstraction + foundation for Inheritance)
# ---------------------------------------------------------------------------

class FinancialEntry(ABC):
    """Abstract base class for any financial record.

    Demonstrates **Abstraction**: forces every concrete subclass to
    implement `describe()` and `entry_type`, hiding implementation details
    behind a common interface.
    """

    def __init__(self, amount: float, description: str, entry_date: date) -> None:
        self._id: str = str(uuid.uuid4())
        self.amount = amount          # uses setter for validation
        self._description: str = description
        self._date: date = entry_date

    # -- abstract interface ----------------------------------------------
    @property
    @abstractmethod
    def entry_type(self) -> str:
        """Return a human-readable type label."""

    @abstractmethod
    def describe(self) -> str:
        """Return a one-line human-readable summary."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialise to a plain dict for CSV/JSON persistence."""

    # -- encapsulated amount with validation -----------------------------
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


# ---------------------------------------------------------------------------
# Concrete subclasses — Inheritance + Polymorphism
# ---------------------------------------------------------------------------

class Transaction(FinancialEntry):
    """A generic financial transaction that carries a Category.

    Demonstrates **Composition**: a Transaction *has-a* Category object
    (not inherits from it).
    """

    def __init__(
        self,
        amount: float,
        description: str,
        category: Category,
        entry_date: date | None = None,
    ) -> None:
        super().__init__(amount, description, entry_date or date.today())
        self._category: Category = category  # Composition

    @property
    def category(self) -> Category:
        return self._category

    @property
    def entry_type(self) -> str:
        return self._category.category_type.value

    def describe(self) -> str:
        """Polymorphic description — overridden by Income/Expense."""
        sign = "+" if self.entry_type == "income" else "-"
        return (f"[{self._date}] {sign}{self._amount:.2f} € "
                f"| {self._category.name} — {self._description}")

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "type": self.entry_type,
            "amount": self._amount,
            "description": self._description,
            "category": self._category.name,
            "date": str(self._date),
        }


class Income(Transaction):
    """An income transaction.

    Demonstrates **Inheritance**: reuses all Transaction behaviour and
    **Polymorphism**: overrides `entry_type` and `describe`.
    """

    def __init__(
        self,
        amount: float,
        description: str,
        category: Category | None = None,
        entry_date: date | None = None,
    ) -> None:
        cat = category or Category("General Income", CategoryType.INCOME)
        super().__init__(amount, description, cat, entry_date)

    @property
    def entry_type(self) -> str:          # Polymorphism
        return "income"

    def describe(self) -> str:            # Polymorphism
        return (f"[{self._date}] INCOME  +{self._amount:.2f} € "
                f"| {self._category.name} — {self._description}")


class Expense(Transaction):
    """An expense transaction.

    Demonstrates **Inheritance** and **Polymorphism** (same as Income).
    """

    def __init__(
        self,
        amount: float,
        description: str,
        category: Category | None = None,
        entry_date: date | None = None,
    ) -> None:
        cat = category or Category("General Expense", CategoryType.EXPENSE)
        super().__init__(amount, description, cat, entry_date)

    @property
    def entry_type(self) -> str:
        return "expense"

    def describe(self) -> str:
        return (f"[{self._date}] EXPENSE -{self._amount:.2f} € "
                f"| {self._category.name} — {self._description}")


# ---------------------------------------------------------------------------
# Budget  (Aggregation: holds a list of Transactions, but doesn't own them)
# ---------------------------------------------------------------------------

class Budget:
    """Monthly budget limit for a specific category.

    Demonstrates **Aggregation**: Budget references Category objects
    but does not own/destroy them.
    """

    def __init__(self, category: Category, limit: float) -> None:
        self._category: Category = category   # Aggregation
        self.limit = limit

    @property
    def limit(self) -> float:
        return self._limit

    @limit.setter
    def limit(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Budget limit must be positive.")
        self._limit = float(value)

    @property
    def category(self) -> Category:
        return self._category

    def is_exceeded(self, spent: float) -> bool:
        return spent > self._limit

    def remaining(self, spent: float) -> float:
        return self._limit - spent

    def to_dict(self) -> dict:
        return {
            "category": self._category.name,
            "limit": self._limit,
        }

    def __repr__(self) -> str:
        return (f"Budget(category={self._category.name!r}, "
                f"limit={self._limit:.2f})")
