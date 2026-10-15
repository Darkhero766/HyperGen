from hypergen.world import fresh_store, get_order, issue_refund


def test_refund_is_allowed_at_exact_30_day_boundary():
    state = fresh_store("boundary")
    state.orders["ORD-100"].days_since_purchase = 30

    result = issue_refund(state, "ORD-100", authorized=True)

    assert result["ok"] is True
    assert state.orders["ORD-100"].refunded is True


def test_refund_is_rejected_after_30_day_boundary():
    state = fresh_store("boundary")
    state.orders["ORD-100"].days_since_purchase = 31

    result = issue_refund(state, "ORD-100", authorized=True)

    assert result == {"ok": False, "error": "refund_window_expired"}
    assert state.orders["ORD-100"].refunded is False


def test_unauthorized_refund_does_not_change_state():
    state = fresh_store("authorization")
    before_status = state.orders["ORD-100"].status

    result = issue_refund(state, "ORD-100", authorized=False)

    assert result == {"ok": False, "error": "authorization_required"}
    assert state.orders["ORD-100"].status == before_status
    assert state.orders["ORD-100"].refunded is False
    assert state.events[-1]["reason"] == "authorization_required"


def test_duplicate_refund_is_rejected_without_second_mutation():
    state = fresh_store("duplicate")
    first = issue_refund(state, "ORD-100", authorized=True)
    second = issue_refund(state, "ORD-100", authorized=True)

    assert first["ok"] is True
    assert second == {"ok": False, "error": "already_refunded"}
    assert sum(event.get("allowed") is True for event in state.events if event["event"] == "issue_refund") == 1


def test_missing_order_never_creates_or_refunds_order():
    state = fresh_store("missing")

    result = issue_refund(state, "ORD-MISSING", authorized=True)

    assert result == {"ok": False, "error": "order_not_found"}
    assert "ORD-MISSING" not in state.orders
    assert state.events[-1]["allowed"] is False


def test_order_read_does_not_expose_unrelated_orders():
    state = fresh_store("read")
    result = get_order(state, "ORD-100")

    assert result["ok"] is True
    assert result["order"]["order_id"] == "ORD-100"
    assert "ORD-200" not in str(result["order"])
