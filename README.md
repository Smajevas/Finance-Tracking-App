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

1. Encapsulation
   Private attribute, only accessible through a property
```python

self._name: str = self._validate_name(name)

@property
def name(self) -> str:
    return self._name
```
The `amount` attribute also uses a setter that rejects invalid values
```python
@amount.setter
def amount(self, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError("Amount must be a number.")
    if value <= 0:
        raise ValueError("Amount must be a positive number.")
    self._amount = float(value)
```
---
2. Abstraction
Forces subclasses to implement methods
```python

class FinancialEntry(ABC):

    @abstractmethod
    def describe(self) -> str:
        pass

    @abstractmethod
    def entry_type(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

`FinancialEntry` cannot be created directly — it forces every subclass to implement `describe()`, `entry_type`, and `to_dict()`.
```
---
3. Inheritance
Income and Expense inherit from Transaction
```python
# Full inheritance chain:
# FinancialEntry (ABC) -> Transaction -> Income
#                                     -> Expense

class Income(Transaction):
    def __init__(self, amount, description, category=None, entry_date=None):
        cat = category or Category("General Income", CategoryType.INCOME)
        super().__init__(amount, description, cat, entry_date)  # calls Transaction.__init__
```
---
4. Polymorphism
The same method name behaves differently depending on which class it belongs to.
```python
# Income.describe() output:
"[2024-06-01] INCOME  +1000.00 € | Salary — Monthly pay"

# Expense.describe() output:
"[2024-06-01] EXPENSE -200.00 € | Food — Groceries"
```
Both classes have the same `describe()` method but produce different results. The tracker can call `.describe()` on any transaction without knowing if it is an `Income` or `Expense`:
```python
for transaction in self._transactions:
    print(transaction.describe())  # works for both Income and Expense
```
---
Composition and Aggregation
Composition
`FinanceTracker` fully owns its transactions — it creates and manages them. If the tracker is gone, the transactions go with it.
```python
class FinanceTracker:
    def __init__(self):
        self._transactions: list[FinancialEntry] = storage.load_transactions()
```
`Transaction` also uses composition — it owns a `Category` object:
```python
class Transaction(FinancialEntry):
    def __init__(self, amount, description, category, entry_date=None):
        self._category: Category = category  # Transaction owns this Category
```
Aggregation
`Budget` references a `Category` object but does not own it — the `Category` can exist independently.
```python
class Budget:
    def __init__(self, category: Category, limit: float):
        self._category: Category = category  # just a reference, not owned
```
---
Design Pattern — Factory Method
The Factory Method pattern centralises the creation of `Income` and `Expense` objects. Instead of writing `if/else` everywhere, a single factory decides which class to create:
```python
class TransactionFactory:
    _creators = {
        "income": IncomeCreator(),
        "expense": ExpenseCreator(),
    }

    @classmethod
    def create(cls, entry_type, amount, description, category_name, entry_date=None):
        creator = cls._creators.get(entry_type.lower())
        return creator.build(amount, description, category_name, entry_date)
```
Why Factory Method?
Adding a new transaction type only requires a new creator class
No need to change existing code
Creation logic is in one place, not scattered everywhere
---
File I/O
All transactions and budgets are saved to and loaded from CSV files automatically:
```python
# Saving transactions to CSV
with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=TRANSACTION_FIELDS)
    writer.writeheader()
    for t in transactions:
        writer.writerow(t.to_dict())

# Loading transactions from CSV
with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        transactions.append(TransactionFactory.from_dict(row))
```
**Factory Method** (`factory.py`) — centralises creation of `Income`/`Expense` objects, enabling new transaction types without modifying existing code.
