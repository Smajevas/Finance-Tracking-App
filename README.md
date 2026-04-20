# Finance Tracker

A command-line personal finance tracking application written in Python,
demonstrating all four OOP pillars, the Factory Method design pattern,
composition/aggregation, CSV file I/O, and unit testing.

## Project Structure
```
finance_tracker/
├── main.py                  # CLI entry point & menu
├── models.py                # Domain models (Category, Transaction, Income, Expense, Budget)
├── factory.py               # Factory Method design pattern
├── tracker.py               # FinanceTracker service class
├── storage.py               # CSV read/write persistence
├── test_finance_tracker.py  # 48 unit tests (unittest)
├── REPORT.md                # Coursework report
└── data/                    # Created at runtime
    ├── transactions.csv
    ├── budgets.csv
    └── summary.txt
```
## How to Run

py main.py

## How to Test

py -m unittest test_finance_tracker -v

## Requirements

- Python 3.10+
- No external packages required

## OOP Pillars Demonstrated

| Pillar | Where |
|---|---|
| Encapsulation | `Category._name`, `FinancialEntry._amount` with property setters |
| Abstraction | `FinancialEntry` ABC with abstract `describe()`, `entry_type`, `to_dict()` |
| Inheritance | `Income` and `Expense` inherit from `Transaction → FinancialEntry` |
| Polymorphism | `describe()` and `entry_type` overridden differently in each subclass |

## Design Pattern

**Factory Method** (`factory.py`) — centralises creation of `Income`/`Expense` objects, enabling new transaction types without modifying existing code.
