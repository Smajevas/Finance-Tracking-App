from __future__ import annotations
from datetime import date
from financial_entry import FinancialEntry
from category import Category

#Inheritance + Polymorphism

class Transaction(FinancialEntry):

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
