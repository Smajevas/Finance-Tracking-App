# Finance Tracker — Coursework Report

## 1. Introduction

### What is this application?

**Finance Tracker** is a command-line Python application that helps users manage their personal finances. Users can record income and expense transactions, organise them by category, set monthly spending budgets, and generate financial summaries. All data is persisted in CSV files so it survives between sessions.

### How to run the program

1. Make sure Python 3.10 or newer is installed.
2. Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/Smajevas/Finance-Tracking-App
```

3. Run the application:

```bash
py main.py
```

4. Run the tests:

```bash
py -m unittest test_finance_tracker -v
```

No third-party packages are required — only the Python standard library.

### How to use the program

After launching, a numbered menu is shown:

```
╔══════════════════════════════════╗
║     FINANCE TRACKER  v1.0        ║
╠══════════════════════════════════╣
║  1. Add Income                   ║
║  2. Add Expense                  ║
║  3. View All Transactions        ║
║  ...                             ║
╚══════════════════════════════════╝
```

Type the number of the desired action and press Enter. The application prompts for any additional details (amount, category, date). Transactions are saved automatically to `data/transactions.csv`.

---

## 2. Body / Analysis
Project Structure
Each class has its own file for clarity and maintainability:
```
finance_tracker/
├── main.py                  # CLI entry point & menu
├── category.py              # Category class + CategoryType
├── financial_entry.py       # Abstract base class
├── transaction.py           # Transaction class
├── income.py                # Income class
├── expense.py               # Expense class
├── budget.py                # Budget class
├── factory.py               # Factory Method design pattern
├── tracker.py               # Main application logic
├── storage.py               # CSV read/write persistence
├── test_finance_tracker.py  # 48 unit tests
└── data/                    # Created at runtime
    ├── transactions.csv
    ├── budgets.csv
    └── summary.txt
```
### OOP Pillars

#### Encapsulation

Bundling data inside a class and restricting direct access using private attributes and properties.

In `category.py`, `_name` is private — it can only be read through the `.name` property, not changed directly from outside:

```python
def __init__(self, name: str, category_type: CategoryType) -> None:
    self._name: str = self._validate_name(name)  # private

@property
def name(self) -> str:
    return self._name  # read-only access
```

In `financial_entry.py`, the `amount` setter rejects invalid values:

```python
@amount.setter
def amount(self, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError("Amount must be a number.")
    if value <= 0:
        raise ValueError("Amount must be a positive number.")
    self._amount = float(value)
```

#### Abstraction

Hiding implementation details behind a simple interface using an abstract base class.

`FinancialEntry` in `financial_entry.py` is abstract — it cannot be created directly and forces every subclass to implement `describe()`, `entry_type`, and `to_dict()`:

```python
from abc import ABC, abstractmethod

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
```

#### Inheritance

A class reusing and extending the behaviour of a parent class.

The full inheritance chain is:

```
FinancialEntry (ABC)
    └── Transaction
            ├── Income
            └── Expense
```

`Income` in `income.py` inherits from `Transaction` and calls `super()` to reuse its constructor:

```python
class Income(Transaction):
    def __init__(self, amount, description, category=None, entry_date=None):
        cat = category or Category("General Income", CategoryType.INCOME)
        super().__init__(amount, description, cat, entry_date)
```

#### Polymorphism

The same method name behaves differently depending on which class it belongs to.

`Income` in `income.py` and `Expense` in `expense.py` both override `describe()` and `entry_type`:

```python
# income.py
def describe(self) -> str:
    return f"[{self._date}] INCOME  +{self._amount:.2f} €"

# expense.py
def describe(self) -> str:
    return f"[{self._date}] EXPENSE -{self._amount:.2f} €"
```

The tracker can call `.describe()` on any transaction without knowing if it is Income or Expense:

```python
for transaction in self._transactions:
    print(transaction.describe())  # works for both
```

---

### Design Pattern — Factory Method

**Location:** `factory.py`

#### What it is

The Factory Method pattern defines an interface for creating objects but lets subclasses decide which class to instantiate. A convenience class (`TransactionFactory`) picks the correct creator automatically:

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

#### Why Factory Method?

Without it, every creation point would need:

```python
if entry_type == "income":
    t = Income(...)
elif entry_type == "expense":
    t = Expense(...)
```

With Factory Method, adding a new transaction type only requires a new creator class — no existing code needs to change.

**Compared to alternatives:**
- *Singleton* — not relevant, the concern is object creation not instance count
- *Abstract Factory* — overkill, we only have one product family
- *Builder* — useful for complex construction steps, not needed here

---

### Composition and Aggregation

#### Composition

`FinanceTracker` in `tracker.py` fully owns its transactions — it creates and manages them:

```python
class FinanceTracker:
    def __init__(self):
        self._transactions: list[FinancialEntry] = storage.load_transactions()
```

`Transaction` in `transaction.py` also uses composition — it owns a `Category` object:

```python
self._category: Category = category  # Transaction owns this Category
```

#### Aggregation

`Budget` in `budget.py` references a `Category` but does not own it — the `Category` can exist independently:

```python
class Budget:
    def __init__(self, category: Category, limit: float):
        self._category: Category = category  # just a reference, not owned
```

---

### Reading from File & Writing to File

`storage.py` handles all CSV file operations using Python's built-in `csv` module.

**Writing transactions:**

```python
with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=TRANSACTION_FIELDS)
    writer.writeheader()
    for t in transactions:
        writer.writerow(t.to_dict())
```

**Reading transactions:**

```python
with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        transactions.append(TransactionFactory.from_dict(row))
```

The same pattern applies to `budgets.csv`. A plain text summary can also be exported to `data/summary.txt` via option 12 in the menu.

---

## 3. Results and Summary

### Results

- The application successfully records income and expense transactions, categorises them, and persists data to CSV files that survive between sessions.
- All four OOP pillars are implemented across separate, clearly named files.
- The Factory Method design pattern centralises transaction creation.
- 48 unit tests covering models, factory, service logic, and file I/O all pass with `py -m unittest test_finance_tracker -v`.
- One challenge was managing file paths during testing — solved by patching `storage.TRANSACTIONS_FILE` with a temporary directory, keeping tests fully isolated from real data.

### Conclusions

This coursework achieved its goal of building a functional, well-structured, object-oriented finance tracking application in Python. Each class has its own file, making the project easy to read and navigate. The separation of concerns means each module has one clear responsibility.

**Future prospects:**
- Add a graphical interface using `tkinter` or a web frontend with `Flask`
- Replace CSV storage with an SQLite database for more powerful querying
- Add monthly/yearly reporting and charts using `matplotlib`
- Implement recurring transactions (e.g. monthly salary auto-entry)

---

## 4. Resources

- Python documentation — `abc` module: <https://docs.python.org/3/library/abc.html>
- Python documentation — `csv` module: <https://docs.python.org/3/library/csv.html>
- PEP 8 — Style Guide for Python Code: <https://peps.python.org/pep-0008/>
- Refactoring Guru — Factory Method: <https://refactoring.guru/design-patterns/factory-method>
- Course materials: <https://oop.szturo.online>
- Course materials: <https://oop.szturo.online>
