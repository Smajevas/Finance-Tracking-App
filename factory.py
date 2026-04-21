from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from models import Category, CategoryType, FinancialEntry, Income, Expense, Transaction

# Abstract creator

class TransactionCreator(ABC):

    @abstractmethod
    def create_transaction(
        self,
        amount: float,
        description: str,
        category_name: str,
        entry_date: date | None = None,
    ) -> FinancialEntry:

    def build(
        self,
        amount: float,
        description: str,
        category_name: str,
        entry_date: date | None = None,
    ) -> FinancialEntry:
        transaction = self.create_transaction(
            amount, description, category_name, entry_date
        )
        return transaction


# Concrete creators

class IncomeCreator(TransactionCreator):

    def create_transaction(
        self,
        amount: float,
        description: str,
        category_name: str,
        entry_date: date | None = None,
    ) -> Income:
        cat = Category(category_name, CategoryType.INCOME)
        return Income(amount, description, cat, entry_date)


class ExpenseCreator(TransactionCreator):

    def create_transaction(
        self,
        amount: float,
        description: str,
        category_name: str,
        entry_date: date | None = None,
    ) -> Expense:
        cat = Category(category_name, CategoryType.EXPENSE)
        return Expense(amount, description, cat, entry_date)


# ---------------------------------------------------------------------------
# Convenience facade
# ---------------------------------------------------------------------------

class TransactionFactory:

    _creators: dict[str, TransactionCreator] = {
        "income": IncomeCreator(),
        "expense": ExpenseCreator(),
    }

    @classmethod
    def create(
        cls,
        entry_type: str,
        amount: float,
        description: str,
        category_name: str,
        entry_date: date | None = None,
    ) -> FinancialEntry:
        creator = cls._creators.get(entry_type.lower())
        if creator is None:
            raise ValueError(
                f"Unknown entry type: {entry_type!r}. "
                f"Valid options: {list(cls._creators.keys())}"
            )
        return creator.build(amount, description, category_name, entry_date)

    @classmethod
    def from_dict(cls, data: dict) -> FinancialEntry:
        from datetime import datetime
        entry_date = (
            datetime.strptime(data["date"], "%Y-%m-%d").date()
            if "date" in data and data["date"]
            else None
        )
        return cls.create(
            entry_type=data["type"],
            amount=float(data["amount"]),
            description=data["description"],
            category_name=data["category"],
            entry_date=entry_date,
        )
