from category import Category, CategoryType

# Budget  (Aggregation: holds a list of Transactions, but doesn't own them)

class Budget:
    
    def __init__(self, category: Category, limit: float) -> None:
        self._category: Category = category   # Aggregation
        self.limit = limit

    @property
    def limit(self) -> float:
        return self._limit

    @limit.setter
    def limit(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Budget limit must be positive.")
        self._limit = float(value)

    @property
    def category(self) -> Category:
        return self._category

    def is_exceeded(self, spent: float) -> bool:
        return spent > self._limit

    def remaining(self, spent: float) -> float:
        return self._limit - spent

    def to_dict(self) -> dict:
        return {
            "category": self._category.name,
            "limit": self._limit,
        }

    def __repr__(self) -> str:
        return (f"Budget(category={self._category.name!r}, "
                f"limit={self._limit:.2f})")
