"""
test_finance_tracker.py — Unit tests for the Finance Tracker application.

Run:
    python -m pytest test_finance_tracker.py -v
  or
    python -m unittest test_finance_tracker -v

Covers:
- Model creation and validation (Category, Income, Expense, Budget)
- OOP pillar behaviours (polymorphism, encapsulation, inheritance)
- Factory Method pattern
- FinanceTracker service logic
- File I/O (storage) with temporary files
"""

import csv
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

# Ensure the project root is on sys.path when running from any directory
sys.path.insert(0, str(Path(__file__).parent))

import storage as storage_module
from factory import TransactionFactory, IncomeCreator, ExpenseCreator
from models import (
    Budget, Category, CategoryType, Expense, FinancialEntry, Income, Transaction,
)
from tracker import FinanceTracker


# Category tests

class TestCategory(unittest.TestCase):

    def test_valid_creation(self):
        cat = Category("Food", CategoryType.EXPENSE)
        self.assertEqual(cat.name, "Food")
        self.assertEqual(cat.category_type, CategoryType.EXPENSE)

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Category("", CategoryType.INCOME)

    def test_whitespace_name_raises(self):
        with self.assertRaises(ValueError):
            Category("   ", CategoryType.EXPENSE)

    def test_to_dict(self):
        cat = Category("Salary", CategoryType.INCOME)
        d = cat.to_dict()
        self.assertEqual(d["name"], "Salary")
        self.assertEqual(d["type"], "income")

    def test_name_is_read_only(self):
        cat = Category("Rent", CategoryType.EXPENSE)
        with self.assertRaises(AttributeError):
            cat.name = "Housing"


# Income / Expense tests (Inheritance + Polymorphism)

class TestIncome(unittest.TestCase):

    def test_income_entry_type(self):
        inc = Income(1000.0, "Monthly salary")
        self.assertEqual(inc.entry_type, "income")

    def test_income_describe_contains_plus(self):
        inc = Income(500.0, "Freelance")
        self.assertIn("+", inc.describe())
        self.assertIn("INCOME", inc.describe())

    def test_amount_positive_validation(self):
        with self.assertRaises(ValueError):
            Income(-50.0, "Invalid")

    def test_amount_zero_validation(self):
        with self.assertRaises(ValueError):
            Income(0, "Zero")

    def test_to_dict_keys(self):
        inc = Income(200.0, "Bonus", entry_date=date(2024, 3, 1))
        d = inc.to_dict()
        for key in ("id", "type", "amount", "description", "category", "date"):
            self.assertIn(key, d)

    def test_amount_setter_validates(self):
        inc = Income(100.0, "Test")
        with self.assertRaises(TypeError):
            inc.amount = "hundred"


class TestExpense(unittest.TestCase):

    def test_expense_entry_type(self):
        exp = Expense(50.0, "Groceries")
        self.assertEqual(exp.entry_type, "expense")

    def test_expense_describe_contains_minus(self):
        exp = Expense(50.0, "Groceries")
        self.assertIn("-", exp.describe())
        self.assertIn("EXPENSE", exp.describe())

    def test_inheritance_from_financial_entry(self):
        """Inheritance: Expense must be a FinancialEntry."""
        exp = Expense(30.0, "Bus ticket")
        self.assertIsInstance(exp, FinancialEntry)
        self.assertIsInstance(exp, Transaction)


class TestPolymorphism(unittest.TestCase):

    def test_describe_differs(self):
        inc = Income(1000.0, "Salary")
        exp = Expense(200.0, "Rent")
        self.assertNotEqual(inc.describe(), exp.describe())

    def test_entry_type_differs(self):
        entries: list[FinancialEntry] = [
            Income(100.0, "A"),
            Expense(50.0, "B"),
        ]
        types = [e.entry_type for e in entries]
        self.assertIn("income", types)
        self.assertIn("expense", types)

    def test_to_dict_type_field(self):
        inc = Income(100.0, "A")
        exp = Expense(50.0, "B")
        self.assertEqual(inc.to_dict()["type"], "income")
        self.assertEqual(exp.to_dict()["type"], "expense")


# Budget tests (Aggregation)

class TestBudget(unittest.TestCase):

    def setUp(self):
        self.cat = Category("Food", CategoryType.EXPENSE)
        self.budget = Budget(self.cat, 300.0)

    def test_is_exceeded_true(self):
        self.assertTrue(self.budget.is_exceeded(350.0))

    def test_is_exceeded_false(self):
        self.assertFalse(self.budget.is_exceeded(100.0))

    def test_remaining_positive(self):
        self.assertAlmostEqual(self.budget.remaining(200.0), 100.0)

    def test_remaining_negative_when_exceeded(self):
        self.assertAlmostEqual(self.budget.remaining(400.0), -100.0)

    def test_limit_setter_rejects_negative(self):
        with self.assertRaises(ValueError):
            self.budget.limit = -50.0

    def test_to_dict(self):
        d = self.budget.to_dict()
        self.assertEqual(d["category"], "Food")
        self.assertAlmostEqual(d["limit"], 300.0)


# Factory Method tests

class TestTransactionFactory(unittest.TestCase):

    def test_create_income(self):
        t = TransactionFactory.create("income", 500.0, "Bonus", "Salary")
        self.assertIsInstance(t, Income)

    def test_create_expense(self):
        t = TransactionFactory.create("expense", 80.0, "Dinner", "Food")
        self.assertIsInstance(t, Expense)

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            TransactionFactory.create("savings", 100.0, "Desc", "Cat")

    def test_case_insensitive(self):
        t = TransactionFactory.create("INCOME", 100.0, "Test", "Cat")
        self.assertIsInstance(t, Income)

    def test_from_dict(self):
        data = {
            "type": "expense",
            "amount": "150.0",
            "description": "Electricity",
            "category": "Utilities",
            "date": "2024-01-15",
        }
        t = TransactionFactory.from_dict(data)
        self.assertIsInstance(t, Expense)
        self.assertAlmostEqual(t.amount, 150.0)

    def test_concrete_income_creator(self):
        creator = IncomeCreator()
        t = creator.build(200.0, "Part-time", "Freelance")
        self.assertIsInstance(t, Income)

    def test_concrete_expense_creator(self):
        creator = ExpenseCreator()
        t = creator.build(45.0, "Metro", "Transport")
        self.assertIsInstance(t, Expense)


# FinanceTracker service tests

class TestFinanceTracker(unittest.TestCase):

    def _make_tracker(self):
        with patch.object(storage_module, "load_transactions", return_value=[]), \
             patch.object(storage_module, "load_budgets", return_value=[]):
            return FinanceTracker()

    def _silent_tracker(self):
        tracker = self._make_tracker()
        tracker._save = lambda: None  # silence save side-effects
        return tracker

    def setUp(self):
        self.tracker = self._make_tracker()
        # Silence all file writes during tests
        patcher_tx = patch.object(storage_module, "save_transactions")
        patcher_bg = patch.object(storage_module, "save_budgets")
        self.mock_save_tx = patcher_tx.start()
        self.mock_save_bg = patcher_bg.start()
        self.addCleanup(patcher_tx.stop)
        self.addCleanup(patcher_bg.stop)

    def test_add_income(self):
        t = self.tracker.add_transaction("income", 1000.0, "Salary", "Work")
        self.assertIsInstance(t, Income)
        self.assertEqual(len(self.tracker.get_all_transactions()), 1)

    def test_add_expense(self):
        t = self.tracker.add_transaction("expense", 200.0, "Rent", "Housing")
        self.assertIsInstance(t, Expense)

    def test_total_income(self):
        self.tracker.add_transaction("income", 1000.0, "Salary", "Work")
        self.tracker.add_transaction("income", 500.0, "Bonus", "Work")
        self.assertAlmostEqual(self.tracker.total_income(), 1500.0)

    def test_total_expenses(self):
        self.tracker.add_transaction("expense", 300.0, "Rent", "Housing")
        self.tracker.add_transaction("expense", 50.0, "Food", "Groceries")
        self.assertAlmostEqual(self.tracker.total_expenses(), 350.0)

    def test_balance(self):
        self.tracker.add_transaction("income", 1000.0, "Salary", "Work")
        self.tracker.add_transaction("expense", 400.0, "Rent", "Housing")
        self.assertAlmostEqual(self.tracker.balance(), 600.0)

    def test_filter_by_type(self):
        self.tracker.add_transaction("income", 1000.0, "Salary", "Work")
        self.tracker.add_transaction("expense", 50.0, "Lunch", "Food")
        incomes = self.tracker.filter_by_type("income")
        self.assertEqual(len(incomes), 1)
        self.assertIsInstance(incomes[0], Income)

    def test_filter_by_category(self):
        self.tracker.add_transaction("expense", 100.0, "Cinema", "Entertainment")
        self.tracker.add_transaction("expense", 200.0, "Rent", "Housing")
        results = self.tracker.filter_by_category("Entertainment")
        self.assertEqual(len(results), 1)

    def test_remove_transaction(self):
        t = self.tracker.add_transaction("income", 500.0, "Freelance", "Work")
        self.assertTrue(self.tracker.remove_transaction(t.id[:8]))
        self.assertEqual(len(self.tracker.get_all_transactions()), 0)

    def test_remove_nonexistent_returns_false(self):
        self.assertFalse(self.tracker.remove_transaction("nonexistent"))

    def test_set_budget(self):
        budget = self.tracker.set_budget("Food", 300.0)
        self.assertAlmostEqual(budget.limit, 300.0)
        self.assertEqual(len(self.tracker.get_budgets()), 1)

    def test_budget_status_exceeded(self):
        self.tracker.set_budget("Food", 100.0)
        self.tracker.add_transaction("expense", 150.0, "Groceries", "Food")
        statuses = self.tracker.budget_status()
        self.assertEqual(len(statuses), 1)
        self.assertTrue(statuses[0]["exceeded"])

    def test_budget_status_not_exceeded(self):
        self.tracker.set_budget("Food", 300.0)
        self.tracker.add_transaction("expense", 50.0, "Lunch", "Food")
        statuses = self.tracker.budget_status()
        self.assertFalse(statuses[0]["exceeded"])

    def test_expenses_by_category(self):
        self.tracker.add_transaction("expense", 80.0, "Lunch", "Food")
        self.tracker.add_transaction("expense", 40.0, "Snacks", "Food")
        self.tracker.add_transaction("expense", 200.0, "Rent", "Housing")
        by_cat = self.tracker.expenses_by_category()
        self.assertAlmostEqual(by_cat["Food"], 120.0)
        self.assertAlmostEqual(by_cat["Housing"], 200.0)

    def test_summary_lines_not_empty(self):
        self.tracker.add_transaction("income", 1000.0, "Salary", "Work")
        lines = self.tracker.summary_lines()
        self.assertGreater(len(lines), 0)


# Storage (CSV) tests

class TestStorage(unittest.TestCase):

    def setUp(self):
        # Use a temporary directory for all file I/O
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.original_tx_file = storage_module.TRANSACTIONS_FILE
        self.original_bg_file = storage_module.BUDGETS_FILE
        storage_module.TRANSACTIONS_FILE = (
            Path(self.tmp_dir.name) / "transactions.csv"
        )
        storage_module.BUDGETS_FILE = (
            Path(self.tmp_dir.name) / "budgets.csv"
        )

    def tearDown(self):
        self.tmp_dir.cleanup()
        storage_module.TRANSACTIONS_FILE = self.original_tx_file
        storage_module.BUDGETS_FILE = self.original_bg_file

    def test_save_and_load_transactions(self):
        transactions = [
            Income(1000.0, "Salary", entry_date=date(2024, 1, 1)),
            Expense(200.0, "Rent", entry_date=date(2024, 1, 5)),
        ]
        storage_module.save_transactions(transactions)
        loaded = storage_module.load_transactions()
        self.assertEqual(len(loaded), 2)
        types = {t.entry_type for t in loaded}
        self.assertIn("income", types)
        self.assertIn("expense", types)

    def test_load_missing_file_returns_empty(self):
        result = storage_module.load_transactions()
        self.assertEqual(result, [])

    def test_save_and_load_budgets(self):
        cat = Category("Food", CategoryType.EXPENSE)
        budgets = [Budget(cat, 300.0)]
        storage_module.save_budgets(budgets)
        loaded = storage_module.load_budgets()
        self.assertEqual(len(loaded), 1)
        self.assertAlmostEqual(loaded[0].limit, 300.0)

    def test_amounts_preserved_after_round_trip(self):
        transactions = [Income(1234.56, "Precise", entry_date=date(2024, 6, 15))]
        storage_module.save_transactions(transactions)
        loaded = storage_module.load_transactions()
        self.assertAlmostEqual(loaded[0].amount, 1234.56, places=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
