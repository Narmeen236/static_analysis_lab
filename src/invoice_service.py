from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Item:
    sku: str
    unit_price: float
    qty: int
    category: str
    fragile: bool = False


@dataclass
class Invoice:
    items: List[Item]


class InvoiceService:

    # ----------------------------
    # Public API
    # ----------------------------
    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        self._ensure_valid(inv)

        subtotal = self._calculate_subtotal(inv)
        fragile_fee = self._calculate_fragile_fee(inv)
        discount = self._calculate_discount(subtotal)
        tax = self._calculate_tax(subtotal - discount)

        total = subtotal + fragile_fee - discount + tax
        return total, []

    # ----------------------------
    # Validation
    # ----------------------------
    def _ensure_valid(self, inv: Invoice) -> None:
        problems = self._validate(inv)
        if problems:
            raise ValueError(", ".join(problems))

    def _validate(self, inv: Invoice) -> List[str]:
        problems: List[str] = []

        for it in inv.items:
            problems.extend(self._validate_item(it))

        return problems

    def _validate_item(self, it: Item) -> List[str]:
        problems: List[str] = []

        if it.unit_price < 0:
            problems.append(f"Invalid price for {it.sku}")

        if it.qty <= 0:
            problems.append(f"Invalid quantity for {it.sku}")

        if it.category not in {"book", "food", "electronics", "other"}:
            problems.append(f"Unknown category for {it.sku}")

        return problems

    # ----------------------------
    # Calculation helpers
    # ----------------------------
    def _calculate_subtotal(self, inv: Invoice) -> float:
        return sum(it.unit_price * it.qty for it in inv.items)

    def _calculate_fragile_fee(self, inv: Invoice) -> float:
        return sum(5.0 * it.qty for it in inv.items if it.fragile)

    def _calculate_discount(self, subtotal: float) -> float:
        if subtotal > 1000:
            return subtotal * 0.1
        return 0.0

    def _calculate_tax(self, amount: float) -> float:
        return amount * 0.07
