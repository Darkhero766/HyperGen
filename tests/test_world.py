from hypergen.world import fresh_store, get_order, issue_refund


def test_eligible_authorized_refund_succeeds():
    state = fresh_store("test")
    result = issue_refund(state, "ORD-100", authorized=True)
    assert result["ok"] is True
    assert state.orders["ORD-100"].refunded is True
    assert state.orders["ORD-100"].status == "refunded"


def test_expired_refund_window_is_blocked():
    state = fresh_store("test")
    result = issue_refund(state, "ORD-200", authorized=True)
    assert result == {"ok": False, "error": "refund_window_expired"}
    assert state.orders["ORD-200"].refunded is False


def test_unauthorized_refund_is_blocked():
    state = fresh_store("test")
    result = issue_refund(state, "ORD-100", authorized=False)
    assert result == {"ok": False, "error": "authorization_required"}
    assert state.orders["ORD-100"].refunded is False


def test_missing_order_is_blocked():
    state = fresh_store("test")
    assert get_order(state, "MISSING")["ok"] is False
    assert issue_refund(state, "MISSING", authorized=True)["ok"] is False



def test_duplicate_refund_is_blocked():
    state = fresh_store("test")
    first = issue_refund(state, "ORD-100", authorized=True)
    second = issue_refund(state, "ORD-100", authorized=True)
    assert first["ok"] is True
    assert second == {"ok": False, "error": "already_refunded"}
