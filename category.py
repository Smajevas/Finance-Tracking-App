from enum import Enum

# Enumerations

class CategoryType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


# Category 

class Category:

    def __init__(self, name: str, category_type: CategoryType) -> None:
        self._name: str = self._validate_name(name)
        self._type: CategoryType = category_type

    #private helper
    @staticmethod
    def _validate_name(name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Category name cannot be empty.")
        return name

    @property
    def name(self) -> str:
        return self._name

    @property
    def category_type(self) -> CategoryType:
        return self._type

    def __repr__(self) -> str:
        return f"Category(name={self._name!r}, type={self._type.value!r})"

    def to_dict(self) -> dict:
        return {"name": self._name, "type": self._type.value}
