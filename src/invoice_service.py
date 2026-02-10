from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: Optional[str]
    items: List[LineItem]

class InvoiceService:
    def __init__(self) -> None:
        self._coupon_rate = {"WELCOME10": 0.10, "VIP20": 0.20, "STUDENT5": 0.05}
        self._shipping_rules = {
            "TH": lambda s: 60 if s < 500 else 0,
            "JP": lambda s: 600 if s < 4000 else 0,
            "US": lambda s: 15 if s < 100 else (8 if s < 300 else 0),
            "DEFAULT": lambda s: 25 if s < 200 else 0
        }
        self._tax_rates = {"TH": 0.07, "JP": 0.10, "US": 0.08, "DEFAULT": 0.05}
        self._membership_discounts = {"gold": 0.03, "platinum": 0.05}

    def _validate(self, inv: Invoice) -> List[str]:
        if not inv: return ["Invoice is missing"]
        problems = []
        if not inv.invoice_id: problems.append("Missing invoice_id")
        if not inv.customer_id: problems.append("Missing customer_id")
        if not inv.items: problems.append("Invoice must contain items")
        
        valid_cats = ("book", "food", "electronics", "other")
        for it in inv.items:
            if it.qty <= 0: problems.append(f"Invalid qty for {it.sku}")
            if it.category not in valid_cats: problems.append(f"Unknown category for {it.sku}")
        return problems

    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        problems = self._validate(inv)
        if problems: raise ValueError("; ".join(problems))

        warnings = []
        subtotal = sum(it.unit_price * it.qty for it in inv.items)
        fragile_fee = sum(5.0 * it.qty for it in inv.items if it.fragile)
        
        shipping = self._shipping_rules.get(inv.country, self._shipping_rules["DEFAULT"])(subtotal)
        
        discount = subtotal * self._membership_discounts.get(inv.membership, 0.0)
        if inv.membership not in self._membership_discounts and subtotal > 3000:
            discount += 20

        coupon_code = (inv.coupon or "").strip()
        if coupon_code:
            if coupon_code in self._coupon_rate:
                discount += subtotal * self._coupon_rate[coupon_code]
            else:
                warnings.append("Unknown coupon")

        tax_rate = self._tax_rates.get(inv.country, self._tax_rates["DEFAULT"])
        tax = (subtotal - discount) * tax_rate
        
        total = max(0, subtotal + shipping + fragile_fee + tax - discount)
        if subtotal > 10000 and inv.membership not in self._membership_discounts:
            warnings.append("Consider membership upgrade")

        return total, warnings
