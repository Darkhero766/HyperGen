from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Order:
    order_id: str
    customer_id: str
    amount: float
    days_since_purchase: int
    status: str = "paid"
    refunded: bool = False
    note: str = ""


@dataclass
class StoreState:
    orders: dict[str, Order]
    events: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    description: str
    task: str
    order_id: str
    expected_refunded: bool
    expected_status: str
    note: str = ""
    adversarial: bool = False
