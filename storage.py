from __future__ import annotations
import csv
import logging
import os
from pathlib import Path

from models import Budget, Category, CategoryType, FinancialEntry
from factory import TransactionFactory

logger = logging.getLogger(__name__)

TRANSACTIONS_FILE = Path("data/transactions.csv")
BUDGETS_FILE = Path("data/budgets.csv")

TRANSACTION_FIELDS = ["id", "type", "amount", "description", "category", "date"]
BUDGET_FIELDS = ["category", "limit"]


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# Transactions

def save_transactions(transactions: list[FinancialEntry]) -> None:
    _ensure_dir(TRANSACTIONS_FILE)
    with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=TRANSACTION_FIELDS)
        writer.writeheader()
        for t in transactions:
            writer.writerow(t.to_dict())
    logger.info("Saved %d transaction(s) to %s", len(transactions), TRANSACTIONS_FILE)


def load_transactions() -> list[FinancialEntry]:
    if not TRANSACTIONS_FILE.exists():
        logger.info("No transactions file found — starting fresh.")
        return []

    transactions: list[FinancialEntry] = []
    with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                transactions.append(TransactionFactory.from_dict(row))
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed row %s: %s", row, exc)

    logger.info("Loaded %d transaction(s) from %s", len(transactions), TRANSACTIONS_FILE)
    return transactions

# Budgets

def save_budgets(budgets: list[Budget]) -> None:
    _ensure_dir(BUDGETS_FILE)
    with open(BUDGETS_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=BUDGET_FIELDS)
        writer.writeheader()
        for b in budgets:
            writer.writerow(b.to_dict())
    logger.info("Saved %d budget(s) to %s", len(budgets), BUDGETS_FILE)


def load_budgets() -> list[Budget]:
    if not BUDGETS_FILE.exists():
        return []

    budgets: list[Budget] = []
    with open(BUDGETS_FILE, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                cat = Category(row["category"], CategoryType.EXPENSE)
                budgets.append(Budget(cat, float(row["limit"])))
            except (ValueError, KeyError) as exc:
                logger.warning("Skipping malformed budget row %s: %s", row, exc)

    logger.info("Loaded %d budget(s) from %s", len(budgets), BUDGETS_FILE)
    return budgets


# Export helper (results / summary)

def export_summary(summary_lines: list[str], filepath: str = "data/summary.txt") -> None:
    path = Path(filepath)
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(summary_lines))
    logger.info("Summary exported to %s", path)
