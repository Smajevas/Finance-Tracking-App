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

### OOP Pillars

#### Encapsulation

Encapsulation means bundling data and the methods that operate on it inside a class, and restricting direct access to internal state through access modifiers and properties.

In this project, `Category`, `FinancialEntry`, `Budget`, and other classes use **private attributes** (prefixed with `_`) combined with Python **properties** to expose read-only or validated access:

```python
class Category:
    def __init__(self, name: str, category_type: CategoryType) -> None:
        self._name: str = self._validate_name(name)   # private
        self._type: CategoryType = category_type       # private

    @property
    def name(self) -> str:          # read-only public access
        return self._name
```

The `amount` attribute of `FinancialEntry` uses a **setter** that rejects invalid values:

```python
@amount.setter
def amount(self, value: float) -> None:
    if not isinstance(value, (int, float)):
        raise TypeError("Amount must be a number.")
    if value <= 0:
        raise ValueError("Amount must be a positive number.")
    self._amount = float(value)
```

A unit test verifies that direct assignment to `name` raises `AttributeError`, confirming the encapsulation works correctly.

#### Abstraction

Abstraction hides complex implementation details behind a simplified interface. In Python this is achieved with `abc.ABC` and `@abstractmethod`.

`FinancialEntry` is an **abstract base class** that defines the interface all financial records must implement, without providing implementations for `describe()`, `entry_type`, or `to_dict()`:

```python
from abc import ABC, abstractmethod

class FinancialEntry(ABC):
    @property
    @abstractmethod
    def entry_type(self) -> str:
        """Return a human-readable type label."""

    @abstractmethod
    def describe(self) -> str:
        """Return a one-line human-readable summary."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialise to a plain dict for CSV/JSON persistence."""
```

Client code (e.g. `storage.py`, `tracker.py`) only interacts with the `FinancialEntry` interface and never needs to know whether it holds an `Income` or `Expense` object.

#### Inheritance

Inheritance allows a class to reuse and extend the behaviour of a parent class.

The class hierarchy is:

```
FinancialEntry (ABC)
    └── Transaction
            ├── Income
            └── Expense
```

`Income` and `Expense` inherit all storage attributes (`_id`, `_amount`, `_description`, `_date`) and common logic from `FinancialEntry` via `Transaction`. They call `super().__init__(...)` to delegate initialisation upward:

```python
class Income(Transaction):
    def __init__(self, amount, description, category=None, entry_date=None):
        cat = category or Category("General Income", CategoryType.INCOME)
        super().__init__(amount, description, cat, entry_date)  # Inheritance
```

A test asserts `isinstance(expense, FinancialEntry)` to verify the inheritance chain.

#### Polymorphism

Polymorphism allows different classes to be treated through a common interface while each responds differently to the same method call.

Both `Income` and `Expense` override `entry_type` and `describe()`:

```python
# Income.describe():
"[2024-06-01] INCOME  +1000.00 € | Salary — Monthly pay"

# Expense.describe():
"[2024-06-01] EXPENSE -200.00 € | Food — Groceries"
```

Because `FinanceTracker` holds a `list[FinancialEntry]`, it can call `.describe()` on every item without knowing the concrete type. The `filter_by_type()` method also relies on `entry_type` being polymorphically overridden:

```python
def filter_by_type(self, entry_type: str) -> list[FinancialEntry]:
    return [t for t in self._transactions if t.entry_type == entry_type]
```

---

### Design Pattern — Factory Method

**Pattern chosen:** Factory Method  
**Location:** `factory.py`

#### What it is

The Factory Method pattern defines an interface (`TransactionCreator.create_transaction`) for creating objects, but lets concrete subclasses (`IncomeCreator`, `ExpenseCreator`) decide which class to instantiate. A convenience façade (`TransactionFactory`) delegates to the correct creator automatically.

#### Why Factory Method?

The application needs to create `Income` or `Expense` objects in two situations:
1. When the user adds a new transaction via the menu.
2. When loading records back from CSV.

Without the pattern, every creation point would contain:

```python
if entry_type == "income":
    t = Income(...)
elif entry_type == "expense":
    t = Expense(...)
```

This violates the Open/Closed Principle. With the Factory Method, adding a new transaction type (e.g. `Savings`) only requires a new `SavingsCreator` subclass and a one-line entry in `TransactionFactory._creators`.

**Compared to alternatives:**

- *Singleton* — irrelevant; the concern is object creation, not instance count.
- *Abstract Factory* — overkill here; we have a single product family with two variants.
- *Builder* — useful when construction involves many optional steps; our objects have simple constructors.

```python
class TransactionCreator(ABC):
    @abstractmethod
    def create_transaction(self, amount, description, category_name, entry_date):
        ...

class IncomeCreator(TransactionCreator):
    def create_transaction(self, amount, description, category_name, entry_date):
        cat = Category(category_name, CategoryType.INCOME)
        return Income(amount, description, cat, entry_date)

class TransactionFactory:
    _creators = {"income": IncomeCreator(), "expense": ExpenseCreator()}

    @classmethod
    def create(cls, entry_type, amount, description, category_name, entry_date=None):
        creator = cls._creators.get(entry_type.lower())
        if creator is None:
            raise ValueError(f"Unknown entry type: {entry_type!r}")
        return creator.build(amount, description, category_name, entry_date)
```

---

### Composition and Aggregation

#### Composition

`FinanceTracker` demonstrates **composition** with its `_transactions` list: the tracker creates, owns, and manages every `Transaction` object. If the tracker is destroyed, the transactions (as Python objects) go with it.

```python
class FinanceTracker:
    def __init__(self) -> None:
        self._transactions: list[FinancialEntry] = storage.load_transactions()
```

`Transaction` itself also uses composition: it *has-a* `Category` object that it constructs and owns.

#### Aggregation

`FinanceTracker` demonstrates **aggregation** with `_budgets`: `Budget` objects are associated with the tracker but exist independently — they can be created and passed around outside the tracker.

```python
self._budgets: list[Budget] = storage.load_budgets()
```

`Budget` itself aggregates a `Category` reference:

```python
class Budget:
    def __init__(self, category: Category, limit: float) -> None:
        self._category: Category = category  # Aggregation — not owned
```

The `Category` can exist and be used in multiple `Budget` or `Transaction` objects simultaneously; no single one "owns" it.

---

### Reading from File & Writing to File

`storage.py` handles all CSV I/O using Python's built-in `csv` module.

**Writing transactions:**

```python
def save_transactions(transactions: list[FinancialEntry]) -> None:
    with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=TRANSACTION_FIELDS)
        writer.writeheader()
        for t in transactions:
            writer.writerow(t.to_dict())
```

**Reading transactions:**

```python
def load_transactions() -> list[FinancialEntry]:
    with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            transactions.append(TransactionFactory.from_dict(row))
```

The same pattern is applied to `budgets.csv`. A text summary can be exported to `data/summary.txt` via option 12 in the menu.

---

## 3. Results and Summary

### Results

- The application successfully records income and expense transactions, categories them, and persists data to CSV files that survive between sessions.
- All four OOP pillars (Encapsulation, Abstraction, Inheritance, Polymorphism) are explicitly implemented and are each testable independently.
- The Factory Method design pattern centralises transaction creation and makes adding new types straightforward without changing existing code.
- 48 unit tests covering models, factory, service logic, and file I/O all pass consistently with `python -m unittest`.
- One challenge was managing the file path during testing — solved by patching `storage.TRANSACTIONS_FILE` with a `tempfile.TemporaryDirectory`, keeping tests fully isolated from the real filesystem.

### Conclusions

This coursework achieved its goal of building a functional, object-oriented finance tracking application in Python. The program demonstrates clean separation of concerns: `models.py` for domain logic, `factory.py` for object creation, `storage.py` for persistence, `tracker.py` for application service logic, and `main.py` for the user interface.

The result is a maintainable codebase where each module has a single responsibility, making it easy to extend — for example, adding a graphical interface, a database backend, or new transaction types.

**Future prospects:**

- Add a graphical interface using `tkinter` or a web frontend with `Flask`.
- Replace CSV storage with an SQLite database for more powerful querying.
- Add monthly/yearly reporting and visualisation (e.g. using `matplotlib`).
- Implement recurring transactions (e.g. monthly salary auto-entry).

---

## 4. Resources

- Python documentation — `abc` module: <https://docs.python.org/3/library/abc.html>
- Python documentation — `csv` module: <https://docs.python.org/3/library/csv.html>
- PEP 8 — Style Guide for Python Code: <https://peps.python.org/pep-0008/>
- Refactoring Guru — Factory Method: <https://refactoring.guru/design-patterns/factory-method>
- Course materials: <https://oop.szturo.online>
