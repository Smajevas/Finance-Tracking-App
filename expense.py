from __future__ import annotations
from datetime import date
from transaction import Transaction
from category import Category, CategoryType

class Expense(Transaction):

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

