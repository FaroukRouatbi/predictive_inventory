from enum import Enum


class TransactionType(str, Enum):
    SALE = "SALE"
    RETURN = "RETURN"
    RESTOCK = "RESTOCK"
    ADJUSTMENT = "ADJUSTMENT"

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BEAUTY = "beauty"
    HOME = "home"
    SPORTS = "sports"
    OTHER = "other"


class Currency(str, Enum):
    USD = "USD"
    CAD = "CAD"
    EUR = "EUR"