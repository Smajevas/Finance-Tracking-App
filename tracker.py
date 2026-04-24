from __future__ import annotations
import logging
from datetime import date

from budget import Budget
from category import Category, CategoryType
from financial_entry import FinancialEntry
from income import Income
from expense import Expense
from factory import TransactionFactory
import storage

logger = logging.getLogger(__name__)


class FinanceTracker:

    def __init__(self) -> None:
        # Composition — tracker owns these transactions
        self._transactions: list[FinancialEntry] = storage.load_transactions()
        # Aggregation — budgets are associated, not owned
        self._budgets: list[Budget] = storage.load_budgets()

    # Transaction management

    def add_transaction(
        self,
        entry_type: str,
        amount: float,
        description: str,
        category_name: str,
        entry_date: date | None = None,
    ) -> FinancialEntry:
        transaction = TransactionFactory.create(
            entry_type, amount, description, category_name, entry_date
        )
        self._transactions.append(transaction)
        storage.save_transactions(self._transactions)
        logger.info("Added transaction: %s", transaction.describe())
        return transaction

    def remove_transaction(self, transaction_id: str) -> bool:
        original_count = len(self._transactions)
        self._transactions = [
            t for t in self._transactions if not t.id.startswith(transaction_id)
        ]
        removed = len(self._transactions) < original_count
        if removed:
            storage.save_transactions(self._transactions)
            logger.info("Removed transaction with id prefix: %s", transaction_id)
        return removed

    def get_all_transactions(self) -> list[FinancialEntry]:
        return list(self._transactions)

    def filter_by_type(self, entry_type: str) -> list[FinancialEntry]:
        return [t for t in self._transactions if t.entry_type == entry_type.lower()]

    def filter_by_category(self, category_name: str) -> list[FinancialEntry]:
        return [
            t for t in self._transactions
            if t.category.name.lower() == category_name.lower()
        ]

    def filter_by_date_range(
        self, start: date, end: date
    ) -> list[FinancialEntry]:
        return [t for t in self._transactions if start <= t.date <= end]

    # Financial calculations

    def total_income(self) -> float:
        return sum(t.amount for t in self._transactions if t.entry_type == "income")

    def total_expenses(self) -> float:
        return sum(t.amount for t in self._transactions if t.entry_type == "expense")

    def balance(self) -> float:
        return self.total_income() - self.total_expenses()

    def expenses_by_category(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for t in self._transactions:
            if t.entry_type == "expense":
                result[t.category.name] = result.get(t.category.name, 0.0) + t.amount
        return result

    # Budget management

    def set_budget(self, category_name: str, limit: float) -> Budget:
        # Remove existing budget for this category if present
        self._budgets = [
            b for b in self._budgets
            if b.category.name.lower() != category_name.lower()
        ]
        cat = Category(category_name, CategoryType.EXPENSE)
        budget = Budget(cat, limit)
        self._budgets.append(budget)
        storage.save_budgets(self._budgets)
        logger.info("Budget set: %s = %.2f €", category_name, limit)
        return budget

    def get_budgets(self) -> list[Budget]:
        return list(self._budgets)

    def budget_status(self) -> list[dict]:
        spent_map = self.expenses_by_category()
        status = []
        for budget in self._budgets:
            spent = spent_map.get(budget.category.name, 0.0)
            status.append({
                "category": budget.category.name,
                "limit": budget.limit,
                "spent": spent,
                "remaining": budget.remaining(spent),
                "exceeded": budget.is_exceeded(spent),
            })
        return status

    # Summary / export

    def summary_lines(self) -> list[str]:
        lines = [
            "=" * 50,
            "  FINANCE TRACKER — SUMMARY",
            "=" * 50,
            f"  Total Income:   {self.total_income():>10.2f} €",
            f"  Total Expenses: {self.total_expenses():>10.2f} €",
            f"  Balance:        {self.balance():>10.2f} €",
            "",
            "  Expenses by category:",
        ]
        for cat, amount in self.expenses_by_category().items():
            lines.append(f"    {cat:<20} {amount:>8.2f} €")

        budget_statuses = self.budget_status()
        if budget_statuses:
            lines += ["", "  Budget status:"]
            for s in budget_statuses:
                flag = "⚠ EXCEEDED" if s["exceeded"] else "✓ ok"
                lines.append(
                    f"    {s['category']:<20} {s['spent']:>7.2f} / "
                    f"{s['limit']:.2f} €  {flag}"
                )
        lines.append("=" * 50)
        return lines

    def export_summary(self) -> None:
        storage.export_summary(self.summary_lines())
        print("Summary exported to data/summary.txt")
