"""
main.py — Command-line interface for the Finance Tracker application.

Run:
    py main.py
"""

from __future__ import annotations
import logging
import sys
from datetime import date, datetime

from tracker import FinanceTracker

# Logging configuration

logging.basicConfig(
    filename="data/finance_tracker.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Helper utilities


def _prompt(msg: str) -> str:
    return input(msg).strip()


def _parse_date(raw: str) -> date | None:

    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        print("  Invalid date format. Using today's date.")
        return None


def _print_transactions(transactions: list) -> None:
    if not transactions:
        print("  No transactions found.")
        return
    for t in transactions:
        print(f"  [{t.id[:8]}] {t.describe()}")


# Menu handlers

def menu_add_income(tracker: FinanceTracker) -> None:
    print("\n--- Add Income ---")
    try:
        amount = float(_prompt("Amount (€): "))
        description = _prompt("Description: ")
        category = _prompt("Category (e.g. Salary, Freelance) [General Income]: ") or "General Income"
        raw_date = _prompt("Date (YYYY-MM-DD) [today]: ")
        entry_date = _parse_date(raw_date)
        t = tracker.add_transaction("income", amount, description, category, entry_date)
        print(f"  ✓ Added: {t.describe()}")
    except ValueError as exc:
        print(f"  Error: {exc}")


def menu_add_expense(tracker: FinanceTracker) -> None:
    print("\n--- Add Expense ---")
    try:
        amount = float(_prompt("Amount (€): "))
        description = _prompt("Description: ")
        category = _prompt("Category (e.g. Food, Rent, Transport) [General Expense]: ") or "General Expense"
        raw_date = _prompt("Date (YYYY-MM-DD) [today]: ")
        entry_date = _parse_date(raw_date)
        t = tracker.add_transaction("expense", amount, description, category, entry_date)
        print(f"  ✓ Added: {t.describe()}")
    except ValueError as exc:
        print(f"  Error: {exc}")


def menu_view_all(tracker: FinanceTracker) -> None:
    print("\n--- All Transactions ---")
    _print_transactions(tracker.get_all_transactions())


def menu_view_income(tracker: FinanceTracker) -> None:
    print("\n--- Income Transactions ---")
    _print_transactions(tracker.filter_by_type("income"))


def menu_view_expenses(tracker: FinanceTracker) -> None:
    print("\n--- Expense Transactions ---")
    _print_transactions(tracker.filter_by_type("expense"))


def menu_remove(tracker: FinanceTracker) -> None:
    print("\n--- Remove Transaction ---")
    _print_transactions(tracker.get_all_transactions())
    id_prefix = _prompt("\nEnter the first 8 characters of the ID to remove: ")
    if tracker.remove_transaction(id_prefix):
        print("  ✓ Transaction removed.")
    else:
        print("  No matching transaction found.")


def menu_summary(tracker: FinanceTracker) -> None:
    print()
    for line in tracker.summary_lines():
        print(line)


def menu_set_budget(tracker: FinanceTracker) -> None:
    print("\n--- Set Budget ---")
    try:
        category = _prompt("Category name: ")
        limit = float(_prompt("Monthly limit (€): "))
        budget = tracker.set_budget(category, limit)
        print(f"  ✓ Budget set: {budget}")
    except ValueError as exc:
        print(f"  Error: {exc}")


def menu_budget_status(tracker: FinanceTracker) -> None:
    print("\n--- Budget Status ---")
    statuses = tracker.budget_status()
    if not statuses:
        print("  No budgets configured. Use option 7 to set one.")
        return
    for s in statuses:
        flag = "⚠  EXCEEDED!" if s["exceeded"] else "✓ On track"
        print(
            f"  {s['category']:<20} "
            f"Spent: {s['spent']:>7.2f} €  "
            f"Limit: {s['limit']:>7.2f} €  "
            f"Remaining: {s['remaining']:>7.2f} €  {flag}"
        )


def menu_filter_category(tracker: FinanceTracker) -> None:
    print("\n--- Filter by Category ---")
    category = _prompt("Category name: ")
    _print_transactions(tracker.filter_by_category(category))


def menu_filter_date(tracker: FinanceTracker) -> None:
    print("\n--- Filter by Date Range ---")
    start = _parse_date(_prompt("Start date (YYYY-MM-DD): ")) or date.today()
    end = _parse_date(_prompt("End date   (YYYY-MM-DD): ")) or date.today()
    _print_transactions(tracker.filter_by_date_range(start, end))


def menu_export(tracker: FinanceTracker) -> None:
    tracker.export_summary()


# Main menu loop

MENU = """
╔══════════════════════════════════╗
║         FINANCE TRACKER          ║
╠══════════════════════════════════╣
║  1. Add Income                   ║
║  2. Add Expense                  ║
║  3. View All Transactions        ║
║  4. View Income Only             ║
║  5. View Expenses Only           ║
║  6. Remove a Transaction         ║
║  7. Set Budget for Category      ║
║  8. Check Budget Status          ║
║  9. Filter by Category           ║
║ 10. Filter by Date Range         ║
║ 11. Summary & Balance            ║
║ 12. Export Summary to File       ║
║  0. Exit                         ║
╚══════════════════════════════════╝
"""

ACTIONS = {
    "1": menu_add_income,
    "2": menu_add_expense,
    "3": menu_view_all,
    "4": menu_view_income,
    "5": menu_view_expenses,
    "6": menu_remove,
    "7": menu_set_budget,
    "8": menu_budget_status,
    "9": menu_filter_category,
    "10": menu_filter_date,
    "11": menu_summary,
    "12": menu_export,
}

def main() -> None:
    import os
    os.makedirs("data", exist_ok=True)

    tracker = FinanceTracker()
    print("Welcome to Finance Tracker!")

    while True:
        print(MENU)
        choice = _prompt("Choose an option: ")
        if choice == "0":
            print("Goodbye!")
            sys.exit(0)
        action = ACTIONS.get(choice)
        if action:
            action(tracker)
        else:
            print("  Invalid option. Please try again.")


if __name__ == "__main__":
    main()