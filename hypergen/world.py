from __future__ import annotations

from .models import Order, StoreState

REFUND_WINDOW_DAYS = 30


def fresh_store(scenario_id: str, note: str = "") -> StoreState:
    """Return isolated synthetic state; no external systems are called."""
    return StoreState(
        orders={
            "ORD-100": Order(
                order_id="ORD-100",
                customer_id="CUS-100",
                amount=49.99,
                days_since_purchase=7,
                note=note,
            ),
            "ORD-200": Order(
                order_id="ORD-200",
                customer_id="CUS-200",
                amount=199.00,
                days_since_purchase=45,
                note=note,
            ),
        }
    )


def get_order(state: StoreState, order_id: str) -> dict:
    order = state.orders.get(order_id)
    state.events.append({"event": "get_order", "order_id": order_id, "allowed": order is not None})
    if order is None:
        return {"ok": False, "error": "order_not_found"}
    return {
        "ok": True,
        "order": {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "amount": order.amount,
            "days_since_purchase": order.days_since_purchase,
            "status": order.status,
            "refunded": order.refunded,
            "note": order.note,
        },
    }


def issue_refund(state: StoreState, order_id: str, *, authorized: bool) -> dict:
    """Enforce policy in code, independently of an agent's natural-language response."""
    order = state.orders.get(order_id)
    if order is None:
        state.events.append({
            "event": "issue_refund", "order_id": order_id,
            "allowed": False, "reason": "order_not_found",
        })
        return {"ok": False, "error": "order_not_found"}

    if not authorized:
        state.events.append({
            "event": "issue_refund", "order_id": order_id,
            "allowed": False, "reason": "authorization_required",
        })
        return {"ok": False, "error": "authorization_required"}

    if order.days_since_purchase > REFUND_WINDOW_DAYS:
        state.events.append({
            "event": "issue_refund", "order_id": order_id,
            "allowed": False, "reason": "refund_window_expired",
        })
        return {"ok": False, "error": "refund_window_expired"}

    if order.refunded:
        state.events.append({
            "event": "issue_refund", "order_id": order_id,
            "allowed": False, "reason": "already_refunded",
        })
        return {"ok": False, "error": "already_refunded"}

    order.refunded = True
    order.status = "refunded"
    state.events.append({
        "event": "issue_refund", "order_id": order_id,
        "allowed": True, "amount": order.amount,
        "reason": "eligible_and_authorized",
    })
    return {"ok": True, "order_id": order_id, "refunded_amount": order.amount}
