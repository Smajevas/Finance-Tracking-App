from __future__ import annotations
from datetime import date
from transaction import Transaction
from category import Category, CategoryType

class Income(Transaction):

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
    